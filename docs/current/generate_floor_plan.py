#!/usr/bin/env python3
"""
30 Park - Ground Floor Plan (v4)

Bottom = front door (south), Top = backyard (north).
Garage attached on far left.

VERIFIED MEASUREMENTS:
- Sunroom (back-left): 10'6" wide × 18'6" deep
- Dining Room (back-right): 11'8" wide × 18'6" deep
- Living room front: 17'0" windows-to-stairs, stairs 3'3" wide
- Living room depth (left): 19'7"
- N-S wall (fireplace wall): 31'7"
- Door dining→den: 45.5" | ~50" opening | 44.25"
- Den: 12' × 12'
- Powder Room: 61" × 61"
- Back closet (bifold): 72" wide × 24" deep
- Closet left of basement stairs: 46" wide × 29" deep
- Basement stairs: ~4'6" wide
- Total depth: 31'2" outside wall to back
- Interior walls: 5.25" | Exterior walls: 6" | Ceiling: 96"
"""

import ezdxf
from ezdxf.enums import TextEntityAlignment
import math

EXT = 6.0
INT = 5.25

# === MAIN DIMENSIONS ===
HOUSE_D = 374.0       # 31'2"

BACK_ROOM_D = 222.0   # 18'6" sunroom & dining room depth
SUNROOM_W = 126.0     # 10'6"
DINING_W = 140.0      # 11'8"
DEN_W = 144.0         # 12'
DEN_D = 144.0         # 12'
POWDER_W = 61.0       # 61"
POWDER_D = 61.0       # 61"
BACK_CLOSET_W = 72.0  # bifold closet
BACK_CLOSET_D = 24.0
BSMT_CLOSET_W = 46.0  # closet left of basement stairs
BSMT_CLOSET_D = 29.0
LR_DEPTH_LEFT = 235.0 # 19'7"
LR_FRONT_TO_STAIRS = 204.0  # 17'0"
STAIR_W = 39.0        # 3'3" main stairs
BSMT_STAIR_W = 54.0   # 4'6" basement stairs

# Derived Y positions
BACK_INT = HOUSE_D - EXT                    # 368
BACK_ROOMS_FRONT = BACK_INT - BACK_ROOM_D   # 146
LR_BACK = EXT + LR_DEPTH_LEFT               # 241

# N-S divider wall (fireplace wall)
LR_TOTAL_W = LR_FRONT_TO_STAIRS + STAIR_W   # 243
NS_W = EXT + LR_TOTAL_W                     # 249 (west face)
NS_E = NS_W + INT                           # 254.25 (east face)

# Main house width (based on right side = dining room width)
HOUSE_W = NS_E + DINING_W + EXT             # 400.25

# Sunroom position
SUN_E = EXT + SUNROOM_W    # 132
SUN_WALL_E = SUN_E + INT   # 137.25

# Kitchen area behind living room
KIT_W = NS_W - SUN_WALL_E  # ~111.75

# Den position (front-right, below dining room)
# Den is 12' × 12' = 144" × 144"
# Right-aligned with dining room (against right exterior wall)
DEN_LEFT = HOUSE_W - EXT - DEN_W            # 250.25
DEN_TOP = EXT + DEN_D                        # 150

# The hallway/corridor is between the N-S wall and the den
HALL_W = DEN_LEFT - NS_E                     # ~-4" -- PROBLEM: den is wider than dining room!

# Since den (12' = 144") > dining room (11'8" = 140"), the den extends 4" past the N-S wall
# This means there's NO separate hallway on the right side — the den fills the space
# OR the den's left wall aligns with the N-S wall and extends 4" past the dining room on the right
# Let's align den's RIGHT wall with dining room's RIGHT wall (against exterior)
# Den left wall: HOUSE_W - EXT - DEN_W = 400.25 - 6 - 144 = 250.25
# Dining room left wall: NS_E = 254.25
# So den extends 4" FURTHER LEFT than the dining room... which means into the N-S wall
# This suggests there might be a hallway between the living room and den on the left side

# Let me reconsider: maybe the den is positioned differently
# Perhaps the hallway runs between the N-S wall and the den, and the den doesn't
# reach the right exterior wall. Or the right exterior wall is further right.
# For now, I'll place the den against the right exterior wall and note the overlap.

# Actually, let me place den left wall at NS_E (aligned with dining room)
# making the den 144" wide starting from NS_E: NS_E + 144 = 398.25
# right exterior wall at 398.25 + 6 = 404.25
# But dining room is 140" from NS_E: NS_E + 140 = 394.25, + 6 = 400.25
# So the house would need to be 4" wider to fit the 12' den...
# OR: the den overlaps with the hallway, powder room, closets within the 140" width
# The den itself might be 12' × 12' with the powder room, hallway carved out of adjacent space

# Simplest approach: make the right side wider to fit the den
# And the dining room has some non-room space (closet?) on its left side
# making the total right-side width = max(DEN_W, DINING_W) = 144"

RIGHT_W = DEN_W  # 144" - the right side is governed by the den width
HOUSE_W = NS_E + RIGHT_W + EXT  # 404.25

# Dining room is 140" within the 144" right side (4" wall/gap on left)
# Actually the dining room might simply be the same right-side width measured differently
# For now: right side = 144" wide, dining room interior = 140" (with a small partition)

# E-W wall between dining room and den
EW_WALL_Y = BACK_ROOMS_FRONT  # 146

# === GARAGE (estimated) ===
GARAGE_W = 240.0   # ~20' wide
GARAGE_D = 264.0   # ~22' deep
GARAGE_X1 = -GARAGE_W - EXT  # far left


def il(v):
    """inches to feet-inches label"""
    f = int(abs(v)) // 12
    r = abs(v) - f * 12
    if r < 0.1: return f"{f}'-0\""
    if abs(r - round(r)) < 0.1: return f"{f}'-{int(round(r))}\""
    return f"{f}'-{r:.1f}\""


def dim(msp, x1, y1, x2, y2, off=18, offset=None):
    if offset is not None:
        off = offset
    if abs(y2-y1) < 0.1:
        d = msp.add_linear_dim(base=(x1,y1-off), p1=(x1,y1), p2=(x2,y2),
                                dimstyle="P30", dxfattribs={"layer":"DIM"})
    elif abs(x2-x1) < 0.1:
        d = msp.add_linear_dim(base=(x1-off,y1), p1=(x1,y1), p2=(x2,y2),
                                angle=90, dimstyle="P30", dxfattribs={"layer":"DIM"})
    else:
        d = msp.add_aligned_dim(p1=(x1,y1), p2=(x2,y2), distance=off,
                                 dimstyle="P30", dxfattribs={"layer":"DIM"})
    d.render()


def t(msp, x, y, s, h=6, layer="RM"):
    msp.add_text(s, height=h, dxfattribs={"layer":layer}
                 ).set_placement((x,y), align=TextEntityAlignment.MIDDLE_CENTER)


def win(msp, x1, y1, x2, y2):
    msp.add_line((x1,y1),(x2,y2), dxfattribs={"layer":"WIN","lineweight":35})
    dx,dy = x2-x1, y2-y1
    ln = max(math.sqrt(dx*dx+dy*dy), 0.01)
    nx,ny = -dy/ln*2, dx/ln*2
    msp.add_line((x1+nx,y1+ny),(x2+nx,y2+ny), dxfattribs={"layer":"WIN"})
    msp.add_line((x1-nx,y1-ny),(x2-nx,y2-ny), dxfattribs={"layer":"WIN"})


def strs(msp, x, y, w, h, n=13, txt="UP"):
    msp.add_lwpolyline([(x,y),(x+w,y),(x+w,y+h),(x,y+h)], close=True, dxfattribs={"layer":"STR"})
    for i in range(1,n):
        msp.add_line((x,y+i*h/n),(x+w,y+i*h/n), dxfattribs={"layer":"STR"})
    mx = x+w/2
    msp.add_line((mx,y+h*0.3),(mx,y+h*0.7), dxfattribs={"layer":"STR"})
    d = 1 if txt == "UP" else -1
    tip = y+h*0.7 if d > 0 else y+h*0.3
    msp.add_line((mx,tip),(mx-4,tip-d*6), dxfattribs={"layer":"STR"})
    msp.add_line((mx,tip),(mx+4,tip-d*6), dxfattribs={"layer":"STR"})
    t(msp, mx, y+h*(0.15 if d>0 else 0.85), txt, 4, "STR")


def fp_sym(msp, x, y, w, d):
    msp.add_lwpolyline([(x,y),(x+w,y),(x+w,y+d),(x,y+d)], close=True, dxfattribs={"layer":"FP"})
    m=0.15
    msp.add_lwpolyline([(x+w*m,y+d*0.1),(x+w*(1-m),y+d*0.1),
                         (x+w*(1-m),y+d*0.9),(x+w*m,y+d*0.9)],
                        close=True, dxfattribs={"layer":"FP"})


def rect(msp, x, y, w, h, layer="INT"):
    msp.add_lwpolyline([(x,y),(x+w,y),(x+w,y+h),(x,y+h)], close=True, dxfattribs={"layer":layer})


def generate():
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    for nm, c, lw in [
        ("EXT",7,50),("INT",7,35),("DOORS",30,18),("WIN",5,25),
        ("FP",1,25),("STR",8,13),("FIX",6,13),("DIM",3,13),
        ("RM",2,13),("DMS",3,13),("NT",8,13),("GAR",9,35),
    ]:
        doc.layers.add(nm, color=c, lineweight=lw)

    doc.dimstyles.new("P30", dxfattribs={
        "dimtxt":4,"dimasz":3,"dimexe":2,"dimexo":2,"dimgap":1.5,"dimlfac":1/12})

    # ==================================================================
    # MAIN HOUSE EXTERIOR
    # ==================================================================
    rect(msp, 0, 0, HOUSE_W, HOUSE_D, "EXT")
    rect(msp, EXT, EXT, HOUSE_W-2*EXT, HOUSE_D-2*EXT, "EXT")

    # ==================================================================
    # GARAGE (far left, attached)
    # ==================================================================
    gx = GARAGE_X1
    rect(msp, gx-EXT, -EXT, GARAGE_W+2*EXT, GARAGE_D+2*EXT, "GAR")
    rect(msp, gx, 0, GARAGE_W, GARAGE_D, "GAR")
    t(msp, gx+GARAGE_W/2, GARAGE_D/2+10, "GARAGE", 8, "GAR")
    t(msp, gx+GARAGE_W/2, GARAGE_D/2-5, "(dims TBD)", 4, "GAR")
    # Connect garage to main house
    msp.add_line((-EXT, -EXT), (0, -EXT), dxfattribs={"layer":"EXT"})
    msp.add_line((-EXT, GARAGE_D+EXT), (0, GARAGE_D+EXT), dxfattribs={"layer":"EXT"})
    # Garage door opening from basement stair area
    msp.add_line((-EXT, EXT+20), (-EXT, EXT+56), dxfattribs={"layer":"DOORS"})

    # ==================================================================
    # CLOSET LEFT OF BASEMENT STAIRS (46" × 29")
    # ==================================================================
    bsmt_cl_x = EXT
    bsmt_cl_y = EXT
    rect(msp, bsmt_cl_x, bsmt_cl_y, BSMT_CLOSET_W, BSMT_CLOSET_D, "INT")
    t(msp, bsmt_cl_x+BSMT_CLOSET_W/2, bsmt_cl_y+BSMT_CLOSET_D/2+5, "OLD PANTRY", 3, "RM")
    t(msp, bsmt_cl_x+BSMT_CLOSET_W/2, bsmt_cl_y+BSMT_CLOSET_D/2-4,
      f"{il(BSMT_CLOSET_W)}x{il(BSMT_CLOSET_D)}", 2.5, "DMS")

    # ==================================================================
    # BASEMENT STAIRS (to right of closet, going down)
    # ==================================================================
    bsmt_x = bsmt_cl_x + BSMT_CLOSET_W + INT
    bsmt_y = EXT + 6
    bsmt_run = 96  # ~8' run estimate
    strs(msp, bsmt_x, bsmt_y, BSMT_STAIR_W, bsmt_run, 11, "DN")
    t(msp, bsmt_x+BSMT_STAIR_W/2, bsmt_y+bsmt_run+10, "BSMT\nSTAIRS", 3.5, "RM")

    # ==================================================================
    # N-S DIVIDER WALL (fireplace wall)
    # ==================================================================
    rect(msp, NS_W, EXT, INT, BACK_INT-EXT, "INT")

    # ==================================================================
    # BACK ROOMS FRONT WALL (E-W, right side: dining↔den)
    # ==================================================================
    # Door opening: 45.5" left + ~50" opening + 44.25" right
    door_l_end = NS_E + 45.5
    door_r_start = HOUSE_W - EXT - 44.25

    rect(msp, NS_E, EW_WALL_Y-INT, 45.5, INT, "INT")           # left wall stub
    rect(msp, door_r_start, EW_WALL_Y-INT, 44.25, INT, "INT")   # right wall stub
    msp.add_line((door_l_end, EW_WALL_Y-INT/2), (door_r_start, EW_WALL_Y-INT/2),
                 dxfattribs={"layer":"DOORS"})

    # ==================================================================
    # LEFT SIDE WALLS
    # ==================================================================
    # E-W wall: living room back wall (left portion, at y=LR_BACK)
    rect(msp, EXT, LR_BACK-INT, SUN_E-EXT, INT, "INT")

    # Sunroom east wall (N-S, from back rooms front to back)
    rect(msp, SUN_E, BACK_ROOMS_FRONT, INT, BACK_INT-BACK_ROOMS_FRONT, "INT")

    # Sunroom east wall extension (from living room back to back rooms front)
    rect(msp, SUN_E, LR_BACK, INT, BACK_ROOMS_FRONT-LR_BACK, "INT")

    # E-W wall behind living room (from sunroom east wall to N-S wall)
    # With opening for kitchen access (~5' opening in center)
    mid = (SUN_WALL_E + NS_W) / 2
    opening = 60
    rect(msp, SUN_WALL_E, LR_BACK-INT, mid-opening/2-SUN_WALL_E, INT, "INT")
    rect(msp, mid+opening/2, LR_BACK-INT, NS_W-mid-opening/2, INT, "INT")

    # ==================================================================
    # DEN AREA (front-right: 12' × 12')
    # ==================================================================
    # Den occupies the right portion of the front-right area
    # Position: right-aligned with exterior wall
    den_x = HOUSE_W - EXT - DEN_W   # 254.25 (right-aligned)
    den_y = EXT                       # from front interior

    # Den north wall (if different from the dining→den wall)
    # The dining→den wall is at y=146, but den is only 12'=144" deep
    # So den top = EXT + 144 = 150, which is 4" higher than the dining wall at 146
    # This means there's a small gap / the den doesn't quite reach the dining room wall
    # I'll draw the den walls explicitly

    # Den left wall (N-S wall separating den from hallway)
    # The space between NS_E (254.25) and den_x might be hallway
    # If den_x = 254.25 (= NS_E), the den starts right at the N-S wall
    # But den is 144" wide and the right side space is 144" (HOUSE_W-EXT-NS_E = 144)
    # So den fills the entire right side with no separate hallway
    # The hallway, powder room, and closet must be carved out of OR adjacent to the den

    # Actually: the den is 12'×12' but the total right-side space is 144" wide × ~140" deep
    # The powder room (61"×61"), hallway, and closet are carved from within this area
    # OR they're on the LEFT side of the N-S wall (in the living room area)

    # From the photos, the hallway with powder room and closets is accessed from the
    # living room side. So the hallway is on the LEFT of the N-S wall, not the right.
    # The den is the full right-side front room.

    # Den north wall at y = EXT + DEN_D = 150
    # Slight gap to dining/den doorway wall at y=146
    # The door wall at y=146 and den top at y=150 don't align.
    # Solution: the den might be 12' measured to the dining room wall:
    # DEN_D = EW_WALL_Y - INT - EXT = 146 - 5.25 - 6 = 134.75"
    # But user said 12' × 12' = 144" × 144"
    # The 12' might be approximate, or include wall thickness
    # For now, I'll use 12' = 144" and draw the den from y=EXT to y=EXT+144=150

    # ==================================================================
    # POWDER ROOM (61" × 61") - off hallway, left side of N-S wall
    # ==================================================================
    # Place powder room in the front area, left of the N-S wall
    # Between the basement stairs area and the staircase going up
    pr_x = bsmt_x + BSMT_STAIR_W + INT  # after basement stairs
    pr_y = EXT
    rect(msp, pr_x, pr_y, POWDER_W, POWDER_D, "INT")
    t(msp, pr_x+POWDER_W/2, pr_y+POWDER_D/2+8, "POWDER", 3.5, "RM")
    t(msp, pr_x+POWDER_W/2, pr_y+POWDER_D/2-2, "ROOM", 3.5, "RM")
    t(msp, pr_x+POWDER_W/2, pr_y+POWDER_D/2-12, f"{il(POWDER_W)}x{il(POWDER_D)}", 2.5, "DMS")
    # Powder room door (opening on top/north side)
    msp.add_line((pr_x+10, pr_y+POWDER_D), (pr_x+10+28, pr_y+POWDER_D),
                 dxfattribs={"layer":"DOORS"})

    # ==================================================================
    # BACK CLOSET (bifold, 72" × 24") - in hallway area
    # ==================================================================
    # Place along the back of the hallway area, south of the kitchen
    bc_x = pr_x + POWDER_W + INT + 10
    bc_y = LR_BACK - INT - BACK_CLOSET_D  # against the back wall of the living room
    rect(msp, bc_x, bc_y, BACK_CLOSET_W, BACK_CLOSET_D, "INT")
    t(msp, bc_x+BACK_CLOSET_W/2, bc_y+BACK_CLOSET_D/2+3, "CLOSET", 3, "RM")
    t(msp, bc_x+BACK_CLOSET_W/2, bc_y+BACK_CLOSET_D/2-5,
      f"{il(BACK_CLOSET_W)}x{il(BACK_CLOSET_D)}", 2.5, "DMS")
    # Bifold door indicator
    msp.add_line((bc_x, bc_y), (bc_x+BACK_CLOSET_W, bc_y), dxfattribs={"layer":"DOORS"})

    # ==================================================================
    # MAIN STAIRCASE (going UP, in living room)
    # ==================================================================
    stair_x = EXT + LR_FRONT_TO_STAIRS   # 210
    stair_y = EXT + 12
    stair_run = 108
    strs(msp, stair_x, stair_y, STAIR_W, stair_run, 13, "UP")
    # Landing
    ly = stair_y + stair_run
    rect(msp, stair_x, ly, STAIR_W, STAIR_W, "STR")
    t(msp, stair_x+STAIR_W/2, ly+STAIR_W/2, "LANDING", 3, "STR")

    # ==================================================================
    # FIREPLACES
    # ==================================================================
    fpw, fpd = 72, 22
    fpx = NS_W - fpw - 8
    fpy = LR_BACK - 85
    fp_sym(msp, fpx, fpy, fpw, fpd)
    t(msp, fpx+fpw/2, fpy+fpd/2, "BRICK FP", 3.5, "FP")

    fp2w, fp2d = 60, 20
    fp2x = NS_E + 10
    fp2y = (BACK_ROOMS_FRONT+BACK_INT)/2 - fp2d/2
    fp_sym(msp, fp2x, fp2y, fp2w, fp2d)
    t(msp, fp2x+fp2w/2, fp2y+fp2d/2, "HERRINGBONE\nBRICK FP", 3, "FP")

    # ==================================================================
    # WINDOWS
    # ==================================================================
    win(msp, EXT+12, BACK_INT, SUN_E-12, BACK_INT)       # sunroom back
    win(msp, EXT, BACK_ROOMS_FRONT+30, EXT, BACK_INT-30) # sunroom left
    win(msp, NS_E+20, BACK_INT, HOUSE_W-EXT-20, BACK_INT) # dining back
    win(msp, HOUSE_W-EXT, BACK_ROOMS_FRONT+40, HOUSE_W-EXT, BACK_INT-40) # dining right
    win(msp, EXT, EXT+60, EXT, LR_BACK-60)               # living room left
    win(msp, EXT+24, EXT, EXT+96, EXT)                    # living room front 1
    win(msp, EXT+108, EXT, EXT+180, EXT)                  # living room front 2
    win(msp, den_x+30, EXT, den_x+DEN_W-30, EXT)          # den front
    win(msp, HOUSE_W-EXT, EXT+24, HOUSE_W-EXT, den_y+DEN_D-24) # den right

    # ==================================================================
    # FRONT DOOR
    # ==================================================================
    fd_x = NS_W - 48
    msp.add_line((fd_x, EXT), (fd_x+36, EXT), dxfattribs={"layer":"DOORS"})
    msp.add_arc(center=(fd_x+36,EXT), radius=36, start_angle=90, end_angle=170,
                dxfattribs={"layer":"DOORS"})

    # ==================================================================
    # KITCHEN FIXTURES
    # ==================================================================
    kcx = (SUN_WALL_E+NS_W)/2
    kcy = (LR_BACK+BACK_INT)/2
    cd = 24
    msp.add_lwpolyline([(NS_W-cd,LR_BACK+INT+6),(NS_W,LR_BACK+INT+6),
                         (NS_W,BACK_INT-24),(NS_W-cd,BACK_INT-24)],
                        dxfattribs={"layer":"FIX"})
    msp.add_lwpolyline([(SUN_WALL_E+6,BACK_INT),(NS_W-cd,BACK_INT),
                         (NS_W-cd,BACK_INT-cd),(SUN_WALL_E+6,BACK_INT-cd)],
                        dxfattribs={"layer":"FIX"})
    iw,ih = 48,28
    rect(msp, kcx-iw/2, kcy-ih/2, iw, ih, "FIX")
    t(msp, kcx, kcy, "ISLAND", 3, "FIX")

    # ==================================================================
    # ROOM LABELS
    # ==================================================================
    scx = (EXT+SUN_E)/2
    scy = (BACK_ROOMS_FRONT+BACK_INT)/2
    t(msp, scx, scy+15, "SUNROOM", 7)
    t(msp, scx, scy+2, f"{il(SUNROOM_W)} x {il(BACK_ROOM_D)}", 4.5, "DMS")
    t(msp, scx, scy-12, "(Slate, Arched Win.)", 3.5, "DMS")

    dcx = (NS_E+HOUSE_W-EXT)/2
    dcy = (BACK_ROOMS_FRONT+BACK_INT)/2
    t(msp, dcx, dcy+15, "DINING ROOM", 7)
    t(msp, dcx, dcy+2, f"{il(DINING_W)} x {il(BACK_ROOM_D)}", 4.5, "DMS")
    t(msp, dcx, dcy-12, "(Hardwood, Crown Mold.)", 3.5, "DMS")

    lcx = (EXT+NS_W)/2
    lcy = (EXT+LR_BACK)/2 - 10
    t(msp, lcx, lcy+30, "LIVING ROOM", 8)
    t(msp, lcx, lcy+15, f"~{il(LR_TOTAL_W)} x {il(LR_DEPTH_LEFT)}", 4.5, "DMS")
    t(msp, lcx, lcy, "(Carpet, Crown Molding, Brick FP)", 3.5, "DMS")
    t(msp, lcx, lcy-12, "French Doors to Back Deck", 3.5, "DMS")

    t(msp, kcx, kcy+35, "KITCHEN /", 6)
    t(msp, kcx, kcy+23, "EATING AREA", 6)
    t(msp, kcx, kcy-20, f"~{il(KIT_W)} wide", 4, "DMS")
    t(msp, kcx, kcy-32, "(Tile Floor)", 3.5, "DMS")

    t(msp, den_x+DEN_W/2, EXT+DEN_D/2+15, "DEN", 7)
    t(msp, den_x+DEN_W/2, EXT+DEN_D/2+2, f"{il(DEN_W)} x {il(DEN_D)}", 4.5, "DMS")
    t(msp, den_x+DEN_W/2, EXT+DEN_D/2-12, "(Hardwood)", 3.5, "DMS")

    # ==================================================================
    # DIMENSIONS
    # ==================================================================
    dim(msp, 0, 0, HOUSE_W, 0, offset=48)
    dim(msp, HOUSE_W, 0, HOUSE_W, HOUSE_D, offset=48)
    dim(msp, EXT, BACK_INT, SUN_E, BACK_INT, offset=15)
    dim(msp, EXT, BACK_ROOMS_FRONT, EXT, BACK_INT, offset=-18)
    dim(msp, NS_E, BACK_INT, HOUSE_W-EXT, BACK_INT, offset=15)
    dim(msp, HOUSE_W-EXT, BACK_ROOMS_FRONT, HOUSE_W-EXT, BACK_INT, offset=18)
    dim(msp, EXT, EXT, NS_W, EXT, offset=-22)
    dim(msp, EXT, EXT, EXT, LR_BACK, offset=-22)
    dim(msp, den_x, EXT, HOUSE_W-EXT, EXT, offset=-12)
    dim(msp, HOUSE_W-EXT, EXT, HOUSE_W-EXT, EXT+DEN_D, offset=18)
    dim(msp, EXT, EXT-3, stair_x, EXT-3, offset=8)

    # ==================================================================
    # ORIENTATION & TITLE
    # ==================================================================
    ax = HOUSE_W+30
    ay = HOUSE_D/2
    msp.add_line((ax,ay),(ax,ay+30), dxfattribs={"layer":"RM"})
    msp.add_line((ax,ay+30),(ax-5,ay+22), dxfattribs={"layer":"RM"})
    msp.add_line((ax,ay+30),(ax+5,ay+22), dxfattribs={"layer":"RM"})
    t(msp, ax, ay+38, "N", 8)
    t(msp, HOUSE_W/2, HOUSE_D+15, "BACKYARD (NORTH)", 5, "DMS")
    t(msp, HOUSE_W/2, -20, "FRONT / STREET (SOUTH)", 5, "DMS")
    t(msp, HOUSE_W/2, -45, "30 PARK - GROUND FLOOR PLAN (v4)", 10)
    t(msp, HOUSE_W/2, -60,
      "AS-BUILT | Ceiling 8'-0\" | Int Walls 5-1/4\" | Units: Inches", 4, "DMS")

    # Notes
    nx = HOUSE_W + 25
    for i, n in enumerate([
        "VERIFIED DIMENSIONS:",
        f"  Sunroom: {il(SUNROOM_W)} x {il(BACK_ROOM_D)}",
        f"  Dining Room: {il(DINING_W)} x {il(BACK_ROOM_D)}",
        f"  Den: {il(DEN_W)} x {il(DEN_D)}",
        f"  Powder Room: {il(POWDER_W)} x {il(POWDER_D)}",
        f"  Back Closet: {il(BACK_CLOSET_W)} x {il(BACK_CLOSET_D)}",
        f"  Old Pantry: {il(BSMT_CLOSET_W)} x {il(BSMT_CLOSET_D)}",
        f"  LR front: {il(LR_FRONT_TO_STAIRS)} win-to-stairs",
        f"  Stairs up: {il(STAIR_W)} wide",
        f"  LR depth (left): {il(LR_DEPTH_LEFT)}",
        "  Fireplace wall: 31'-7\"",
        "  Total depth: 31'-2\"",
        "",
        "ITEMS TO VERIFY:",
        "  - Overall house width",
        "  - Kitchen/eating area layout",
        "  - Hallway routing",
        "  - Garage dimensions",
        "  - Closet/powder room positions",
    ]):
        msp.add_text(n, height=3.5, dxfattribs={"layer":"NT"}
                     ).set_placement((nx, 180-i*7), align=TextEntityAlignment.LEFT)

    out = "/home/paul/Data/workspace/PaulLaurie30Park/docs/current/30park-ground-floor-plan.dxf"
    doc.saveas(out)
    print(f"DXF: {out}")
    return out


if __name__ == "__main__":
    generate()
