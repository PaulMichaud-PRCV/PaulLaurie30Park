#!/usr/bin/env python3
"""
Build a clean, draftsperson-quality floor plan from the v16 coordinates.
Produces proper poché walls (filled), stair treads with arrows, distinct
exterior vs interior walls, and clean labeling.

Uses the flipped coordinate system from the original:
  DXF X = North-South (increases North)
  DXF Y = flipped East-West (high Y = West/backyard, low Y = East/front door)
"""
import ezdxf
from ezdxf.enums import TextEntityAlignment
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
import math

# ═══════════════════════════════════════════════════════════════════════════
# COORDINATES (from v16, already flipped: Y=0 is East/front, Y=617.5 is West)
# These are the INTERIOR FACE coordinates of each room.
# ═══════════════════════════════════════════════════════════════════════════
EW = 5.25  # interior wall thickness
XW = 6.0   # exterior wall thickness

# Rooms (X=N-S position, Y=E-W position in flipped coords)
# Format: (x_min, y_min, x_max, y_max) = (south, east, north, west)
SUNROOM    = (495.0, 389.5, 625.0, 611.5)
DINING     = (630.2, 389.5, 770.2, 611.5)
KITCHEN    = (495.0, 239.0, 625.0, 384.2)
PIANO      = (630.2, 246.2, 770.2, 384.2)   # open east to living
LIVING     = (527.2, 6.0, 770.2, 241.0)     # south wall partial
DEN        = (279.0, 54.0, 423.0, 198.0)
EATING     = (240.0, 300.0, 423.0, 426.0)
POWDER     = (362.0, 239.0, 423.0, 300.0)
CLOSET     = (290.0, 276.0, 362.0, 300.0)
PANTRY     = (279.0, 198.0, 325.0, 227.0)
ENTRY      = (423.0, 54.0, 495.0, 198.0)    # approximate; entryway zone
OPEN_SPACE = (423.0, 239.0, 495.0, 426.0)   # open to kitchen/eating
GARAGE_IN  = (0.0, 6.0, 240.0, 384.2)
GARAGE_OUT = (-6.0, 0.0, 240.0, 390.2)

# Stairs
BDRM_STAIR = (495.0, 6.0, 573.0, 102.0)     # main flights
BDRM_LAND  = (501.0, 101.0, 573.0, 139.0)   # landing
LOFT_STAIR = (240.0, 54.0, 279.0, 144.0)

# Fireplace
FIREPLACE  = (612.8, 6.0, 684.8, 28.0)

# ═══════════════════════════════════════════════════════════════════════════

def rect_poly(r):
    """Room tuple to shapely Polygon."""
    return Polygon([(r[0],r[1]),(r[2],r[1]),(r[2],r[3]),(r[0],r[3])])

def wall_band(poly, thickness):
    """Create a wall band (ring) around a polygon."""
    outer = poly.buffer(thickness, join_style=2)  # mitered corners
    return outer.difference(poly)

def poly_to_hatch_path(msp, poly, layer, color):
    """Draw a shapely polygon (possibly with holes) as a solid hatch."""
    if poly.is_empty:
        return
    if isinstance(poly, MultiPolygon):
        for p in poly.geoms:
            poly_to_hatch_path(msp, p, layer, color)
        return
    hatch = msp.add_hatch(color=color, dxfattribs={"layer": layer})
    ext = list(poly.exterior.coords)
    hatch.paths.add_polyline_path(ext, is_closed=True)
    for interior in poly.interiors:
        hatch.paths.add_polyline_path(list(interior.coords), is_closed=True)

def poly_outline(msp, poly, layer):
    """Draw outline of a shapely polygon."""
    if poly.is_empty:
        return
    if isinstance(poly, MultiPolygon):
        for p in poly.geoms:
            poly_outline(msp, p, layer)
        return
    coords = list(poly.exterior.coords)
    msp.add_lwpolyline(coords, close=True, dxfattribs={"layer": layer})

def draw_stair_treads(msp, x1, y1, x2, y2, direction, n_treads, layer):
    """Draw stair treads. direction: 'x' or 'y' for tread line orientation."""
    if direction == 'x':
        # treads run parallel to X axis (perpendicular to Y travel)
        step = (y2 - y1) / n_treads
        for i in range(n_treads + 1):
            y = y1 + i * step
            msp.add_line((x1, y), (x2, y), dxfattribs={"layer": layer})
    else:
        # treads run parallel to Y axis (perpendicular to X travel)
        step = (x2 - x1) / n_treads
        for i in range(n_treads + 1):
            x = x1 + i * step
            msp.add_line((x, y1), (x, y2), dxfattribs={"layer": layer})

def draw_stair_arrow(msp, x, y1, y2, layer):
    """Draw UP arrow along Y direction."""
    mid_y = (y1 + y2) / 2
    # Arrow line
    msp.add_line((x, y1 + (y2-y1)*0.3), (x, y1 + (y2-y1)*0.7),
                 dxfattribs={"layer": layer})
    # Arrowhead (pointing toward y1 = east = bottom = down in view, so UP = toward lower y)
    tip_y = y1 + (y2-y1)*0.3
    ah = 4
    msp.add_line((x, tip_y), (x-ah, tip_y+ah*1.5), dxfattribs={"layer": layer})
    msp.add_line((x, tip_y), (x+ah, tip_y+ah*1.5), dxfattribs={"layer": layer})

def T(msp, x, y, text, height, layer):
    """Add centered text."""
    msp.add_text(text, height=height, dxfattribs={"layer": layer}).set_placement(
        (x, y), align=TextEntityAlignment.MIDDLE_CENTER)


def build():
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    # ── Layers ──
    layers = {
        "WALL-EXT":  (250, 70),   # dark gray fill, thick outline — exterior walls
        "WALL-INT":  (8, 35),     # medium gray, thinner — interior walls
        "WALL-OUT":  (7, 50),     # white outlines for wall edges
        "ROOM":      (7, 13),     # room outlines (light)
        "STAIR":     (7, 25),     # stairs
        "STAIR-FILL":(9, 13),     # stair fill
        "FP":        (1, 25),     # fireplace
        "DOOR":      (30, 18),    # doors
        "TEXT":      (2, 13),     # room names (yellow)
        "DIMS":      (3, 13),     # dimensions text (green)
        "NOTES":     (8, 13),     # notes
        "GARAGE":    (9, 35),     # garage
    }
    for name, (color, lw) in layers.items():
        doc.layers.add(name, color=color, lineweight=lw)

    # ══════════════════════════════════════════════════════════════════════
    # 1. COMPUTE WALL GEOMETRY via Shapely
    # ══════════════════════════════════════════════════════════════════════

    # All floor regions (rooms + circulation)
    floor_rooms = [
        SUNROOM, DINING, KITCHEN, PIANO, LIVING, DEN, EATING,
        POWDER, CLOSET, PANTRY, ENTRY, OPEN_SPACE,
        BDRM_STAIR, BDRM_LAND, LOFT_STAIR,
    ]
    floor_polys = [rect_poly(r) for r in floor_rooms]
    all_floor = unary_union(floor_polys)

    # Close small gaps (interior walls ≤ 6") to get solid interior
    solid_interior = all_floor.buffer(3.5, join_style=2).buffer(-3.5, join_style=2)

    # Interior walls = solid_interior minus actual floor
    interior_walls = solid_interior.difference(all_floor)

    # Exterior walls = band around solid_interior
    exterior_walls = wall_band(solid_interior, XW)

    # ── Draw wall fills (poché) ──
    poly_to_hatch_path(msp, exterior_walls, "WALL-EXT", 250)
    poly_to_hatch_path(msp, interior_walls, "WALL-INT", 8)

    # ── Draw wall outlines ──
    # Exterior outline (thick white)
    outer_boundary = solid_interior.buffer(XW, join_style=2)
    poly_outline(msp, outer_boundary, "WALL-OUT")
    poly_outline(msp, solid_interior, "WALL-OUT")

    # ══════════════════════════════════════════════════════════════════════
    # 2. GARAGE (separate contained rectangle with its own walls)
    # ══════════════════════════════════════════════════════════════════════
    gar_inner = rect_poly(GARAGE_IN)
    gar_outer = rect_poly(GARAGE_OUT)
    gar_walls = gar_outer.difference(gar_inner)
    poly_to_hatch_path(msp, gar_walls, "GARAGE", 9)
    poly_outline(msp, gar_outer, "WALL-OUT")
    poly_outline(msp, gar_inner, "WALL-OUT")

    # ══════════════════════════════════════════════════════════════════════
    # 3. STAIRS — proper treads + arrows
    # ══════════════════════════════════════════════════════════════════════

    # ── Bedroom Stairs (180° double-wide) ──
    bx1, by1, bx2, by2 = BDRM_STAIR
    mid_x = (bx1 + bx2) / 2  # center wall of U-turn (534)

    # Outline
    msp.add_lwpolyline([(bx1,by1),(bx2,by1),(bx2,by2),(bx1,by2)],
                        close=True, dxfattribs={"layer": "STAIR"})
    # Center divider wall
    msp.add_line((mid_x, by1), (mid_x, by2), dxfattribs={"layer": "STAIR"})

    # Treads in south flight (bx1 to mid_x) — travel direction is Y (east-west)
    draw_stair_treads(msp, bx1, by1, mid_x, by2, 'x', 12, "STAIR")
    # Treads in north flight (mid_x to bx2)
    draw_stair_treads(msp, mid_x, by1, bx2, by2, 'x', 12, "STAIR")

    # UP arrows (going toward lower Y = east = up in the house)
    draw_stair_arrow(msp, (bx1+mid_x)/2, by1, by2, "STAIR")
    draw_stair_arrow(msp, (mid_x+bx2)/2, by2, by1, "STAIR")  # reversed for return flight

    # Break line (diagonal zigzag across middle)
    bmid_y = (by1 + by2) / 2
    zw = 6
    for x in [bx1, mid_x, bx2]:
        pass  # skip break line for clarity

    # Landing
    lx1, ly1, lx2, ly2 = BDRM_LAND
    msp.add_lwpolyline([(lx1,ly1),(lx2,ly1),(lx2,ly2),(lx1,ly2)],
                        close=True, dxfattribs={"layer": "STAIR"})

    # ── Loft Stairs ──
    lsx1, lsy1, lsx2, lsy2 = LOFT_STAIR
    msp.add_lwpolyline([(lsx1,lsy1),(lsx2,lsy1),(lsx2,lsy2),(lsx1,lsy2)],
                        close=True, dxfattribs={"layer": "STAIR"})
    # Treads (travel in Y direction)
    draw_stair_treads(msp, lsx1, lsy1, lsx2, lsy2, 'x', 10, "STAIR")
    # UP arrow
    draw_stair_arrow(msp, (lsx1+lsx2)/2, lsy1, lsy2, "STAIR")

    # Stair labels
    T(msp, (bx1+bx2)/2, (by1+by2)/2 - 15, "BEDROOM", 3.5, "TEXT")
    T(msp, (bx1+bx2)/2, (by1+by2)/2 - 8, "STAIRS", 3.5, "TEXT")
    T(msp, (lx1+lx2)/2, (ly1+ly2)/2, "LANDING", 2.5, "STAIR")
    T(msp, (lsx1+lsx2)/2, (lsy1+lsy2)/2 + 8, "LOFT", 3, "TEXT")
    T(msp, (lsx1+lsx2)/2, (lsy1+lsy2)/2, "STAIRS", 3, "TEXT")

    # ══════════════════════════════════════════════════════════════════════
    # 4. FIREPLACE
    # ══════════════════════════════════════════════════════════════════════
    fx1, fy1, fx2, fy2 = FIREPLACE
    # Surround (filled)
    fp_poly = rect_poly(FIREPLACE)
    poly_to_hatch_path(msp, fp_poly, "FP", 1)
    msp.add_lwpolyline([(fx1,fy1),(fx2,fy1),(fx2,fy2),(fx1,fy2)],
                        close=True, dxfattribs={"layer": "FP"})
    # Firebox opening
    inx = (fx2-fx1)*0.15
    iny = (fy2-fy1)*0.15
    msp.add_lwpolyline([
        (fx1+inx, fy1+iny), (fx2-inx, fy1+iny),
        (fx2-inx, fy2-iny), (fx1+inx, fy2-iny)
    ], close=True, dxfattribs={"layer": "FP"})

    # ══════════════════════════════════════════════════════════════════════
    # 5. FRONT DOOR
    # ══════════════════════════════════════════════════════════════════════
    # Door opening in the entry east wall (at y≈102 based on original)
    msp.add_line((423, 102), (495, 102), dxfattribs={"layer": "DOOR"})
    # Door swing arc
    msp.add_arc(center=(495, 102), radius=36, start_angle=90, end_angle=180,
                dxfattribs={"layer": "DOOR"})

    # ══════════════════════════════════════════════════════════════════════
    # 6. ROOM LABELS
    # ══════════════════════════════════════════════════════════════════════
    def room_label(r, name, dims=None, note=None, nh=7):
        cx = (r[0]+r[2])/2
        cy = (r[1]+r[3])/2
        T(msp, cx, cy, name, nh, "TEXT")
        if dims:
            T(msp, cx, cy + nh*2, dims, nh*0.6, "DIMS")
        if note:
            T(msp, cx, cy + nh*3.5, note, nh*0.45, "DIMS")

    room_label(SUNROOM, "SUNROOM", "10'-10\" × 18'-6\"", "(Slate, Arched Windows)")
    room_label(DINING, "DINING ROOM", "11'-8\" × 18'-6\"", "(Hardwood, Crown Molding)")
    room_label(KITCHEN, "KITCHEN", None, "(Tile Floor)")
    room_label(PIANO, "PIANO ROOM", "11'-8\" × 11'-6\"")
    room_label(DEN, "DEN", "12'-0\" × 12'-0\"", "(Hardwood)")
    room_label(EATING, "EATING AREA", "10'-6\" × 15'-3\"", "(Tile, Coffered Ceiling)")
    room_label(POWDER, "POWDER\nROOM", "61\" × 61\"", None, 3.5)
    room_label(CLOSET, "CLOSET", "72\" × 24\"", None, 3)
    room_label(PANTRY, "PANTRY", "46\" × 29\"", None, 3)

    # Living room (large, offset label)
    T(msp, 648.8, 100, "LIVING ROOM", 9, "TEXT")
    T(msp, 648.8, 118, "~20'-3\" × 19'-7\"", 4.5, "DIMS")
    T(msp, 648.8, 132, "(Carpet, Crown Molding)", 3.5, "DIMS")

    # Entry
    T(msp, 459, 126, "ENTRY", 5, "TEXT")

    # Garage
    T(msp, 120, 195, "GARAGE", 8, "TEXT")
    T(msp, 120, 210, "(dims TBD)", 4, "DIMS")

    # Fireplace label
    T(msp, (fx1+fx2)/2, (fy1+fy2)/2, "FIREPLACE", 2.5, "FP")

    # Open to kitchen label
    T(msp, 459, 332, "(open to kitchen)", 3, "DIMS")

    # ══════════════════════════════════════════════════════════════════════
    # 7. COMPASS + ORIENTATION
    # ══════════════════════════════════════════════════════════════════════
    cx, cy = 820, 309
    msp.add_line((cx, cy), (cx+30, cy), dxfattribs={"layer": "TEXT"})
    msp.add_line((cx+30, cy), (cx+22, cy+5), dxfattribs={"layer": "TEXT"})
    msp.add_line((cx+30, cy), (cx+22, cy-5), dxfattribs={"layer": "TEXT"})
    T(msp, cx+40, cy, "N", 8, "TEXT")

    T(msp, 400, -25, "EAST (Front Door / Street)", 5, "DIMS")
    T(msp, 400, 640, "WEST (Backyard)", 5, "DIMS")
    T(msp, -35, 309, "S", 5, "DIMS")
    T(msp, 805, 270, "NORTH", 4, "DIMS")

    # ══════════════════════════════════════════════════════════════════════
    # 8. TITLE BLOCK
    # ══════════════════════════════════════════════════════════════════════
    T(msp, 400, 670, "30 PARK — GROUND FLOOR PLAN", 10, "TEXT")
    T(msp, 400, 685, "As-Built | Front faces EAST | Ceiling 8'-0\" | Int. Walls 5¼\"", 4, "DIMS")

    # ══════════════════════════════════════════════════════════════════════
    # SAVE
    # ══════════════════════════════════════════════════════════════════════
    out = "/home/paul/Data/workspace/PaulLaurie30Park/docs/current/30park-ground-floor-plan.dxf"
    doc.saveas(out)
    print(f"Clean floor plan saved: {out}")
    return out

if __name__ == "__main__":
    build()
