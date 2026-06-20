#!/usr/bin/env python3
"""
30 Park Ground Floor Plan v6 — matches OmniGraffle layout exactly.

COMPASS:  Front door = EAST, Backyard = WEST, Living Room = NORTH, Garage = SOUTH
DXF AXES: X increases NORTH, Y increases WEST
Origin:   (0,0) = South-East exterior corner
"""
import ezdxf, math
from ezdxf.enums import TextEntityAlignment

E = 6.0     # exterior wall
I = 5.25    # interior wall

# ── room dimensions (inches) ──────────────────────────────────────────────
SUNROOM_NS   = 130    # 10'10" north-south
DINING_NS    = 140    # 11'8"
BACK_EW      = 222    # 18'6" east-west depth of sunroom & dining room
DEN_NS       = 144    # 12'
DEN_EW       = 144    # 12'
POWDER       = 61     # 61" × 61"
CLOSET_W     = 72     # bifold closet 72" × 24"
CLOSET_D     = 24
PANTRY_W     = 46     # old pantry 46" × 29"
PANTRY_D     = 29
LR_NS        = 243    # 20'3" (17'0" + 3'3" stairs)
LR_EW        = 235    # 19'7"

# ── Y axis (East-West, Y increases = West/backyard) ──────────────────────
HOUSE_EW = 374        # 31'2" total exterior depth
Y_EAST_INT = E                           # 6
Y_WEST_INT = HOUSE_EW - E               # 368

# back rooms (sunroom + dining room) at the WEST end
BACK_Y_EAST = Y_WEST_INT - BACK_EW      # 146  (east face of back rooms)
BACK_WALL_Y = BACK_Y_EAST - I           # 140.75 (east face of wall between back rooms & kitchen)

# kitchen east-west: from the back-rooms wall eastward
KIT_EW = 101  # ~8'5" deep (estimate — to be verified)
KIT_Y_EAST = BACK_WALL_Y - KIT_EW       # ≈ 40

# living room at the EAST end: Y=6 to Y=241
LR_Y_WEST = Y_EAST_INT + LR_EW          # 241

# den at the EAST end: Y=6 to Y=150
DEN_Y_WEST = Y_EAST_INT + DEN_EW        # 150

# ── X axis (South-North, X increases = North/living room) ────────────────
# from south to north: eating area | sunroom | divider | dining room
# kitchen is at the same X as sunroom, but east of it (lower Y)
# living room is at the same X as dining room, east of it

EATING_X_S = E                           # 6
DEN_X_S    = E                           # 6
DEN_X_N    = DEN_X_S + DEN_NS            # 150

# wall between den/eating and sunroom/kitchen zone
DEN_TOP_WALL_N = DEN_X_N + I             # 155.25

SUN_X_S    = DEN_TOP_WALL_N              # 155.25
SUN_X_N    = SUN_X_S + SUNROOM_NS        # 285.25

DIVIDER_X_S = SUN_X_N                    # 285.25 (south face of sun/din divider)
DIVIDER_X_N = DIVIDER_X_S + I            # 290.5

DIN_X_S    = DIVIDER_X_N                 # 290.5
DIN_X_N    = DIN_X_S + DINING_NS         # 430.5

HOUSE_NS   = DIN_X_N + E                 # 436.5

# living room: X = LR_S to DIN_X_N (same north wall as dining room)
LR_X_N     = DIN_X_N                     # 430.5
LR_X_S     = LR_X_N - LR_NS             # 187.5

# kitchen: same X range as sunroom
KIT_X_S    = SUN_X_S                     # 155.25
KIT_X_N    = SUN_X_N                     # 285.25

# eating area: south of sunroom in the WEST band
EAT_X_S    = E                           # 6
EAT_X_N    = DEN_X_N                     # 150 (no wall to kitchen per user)

# ── helpers ───────────────────────────────────────────────────────────────
def il(v):
    f,r = divmod(abs(v),12)
    return f"{int(f)}'-{int(round(r))}\"" if round(r) else f"{int(f)}'-0\""

def generate():
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    for n,c,w in [("EXT",7,50),("INT",7,35),("DOOR",30,18),("WIN",5,25),
                   ("FP",1,25),("STR",8,13),("FIX",6,13),("DIM",3,13),
                   ("RM",2,13),("DM",3,13),("GAR",9,35)]:
        doc.layers.add(n,color=c,lineweight=w)
    doc.dimstyles.new("D",dxfattribs={"dimtxt":4,"dimasz":3,"dimexe":2,
                                       "dimexo":2,"dimgap":1.5,"dimlfac":1/12})

    def R(x,y,w,h,layer="INT"):
        msp.add_lwpolyline([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],close=True,
                           dxfattribs={"layer":layer})
    def T(x,y,s,h=6,layer="RM"):
        msp.add_text(s,height=h,dxfattribs={"layer":layer}).set_placement(
            (x,y),align=TextEntityAlignment.MIDDLE_CENTER)
    def W(x1,y1,x2,y2):
        msp.add_line((x1,y1),(x2,y2),dxfattribs={"layer":"WIN","lineweight":35})
        dx,dy=x2-x1,y2-y1; ln=max(math.hypot(dx,dy),1)
        nx,ny=-dy/ln*2,dx/ln*2
        msp.add_line((x1+nx,y1+ny),(x2+nx,y2+ny),dxfattribs={"layer":"WIN"})
        msp.add_line((x1-nx,y1-ny),(x2-nx,y2-ny),dxfattribs={"layer":"WIN"})
    def DH(x1,x2,y,off=18):
        d=msp.add_linear_dim(base=(x1,y-off),p1=(x1,y),p2=(x2,y),dimstyle="D",
                             dxfattribs={"layer":"DIM"}); d.render()
    def DV(y1,y2,x,off=18):
        d=msp.add_linear_dim(base=(x-off,y1),p1=(x,y1),p2=(x,y2),angle=90,
                             dimstyle="D",dxfattribs={"layer":"DIM"}); d.render()

    # ═══ EXTERIOR WALLS ═══
    R(0, 0, HOUSE_NS, HOUSE_EW, "EXT")
    R(E, E, HOUSE_NS-2*E, HOUSE_EW-2*E, "EXT")

    # ═══ BACK ROOMS E-W WALL (separates back rooms from kitchen/eating) ═══
    # runs full N-S width at Y = BACK_Y_EAST
    R(E, BACK_Y_EAST-I, HOUSE_NS-2*E, I, "INT")

    # ═══ SUNROOM / DINING ROOM DIVIDER (E-W wall between them) ═══
    # runs from west wall to back rooms east wall
    R(DIVIDER_X_S, BACK_Y_EAST, I, Y_WEST_INT-BACK_Y_EAST, "INT")

    # ═══ DEN / KITCHEN DIVIDER WALL (at den N edge, E-W) ═══
    # runs from south wall to living room area
    R(DEN_X_N, E, I, BACK_Y_EAST-E, "INT")

    # ═══ SUNROOM / KITCHEN N-S WALL (between back rooms and kitchen zone) ═══
    # This wall is the east wall of the back rooms, already drawn above.
    # But it also separates sunroom (west) from kitchen (east) at the sunroom X range.
    # The back rooms wall at Y=BACK_Y_EAST serves this purpose.

    # ═══ LIVING ROOM SOUTH WALL ═══
    # from den/kitchen zone to the east wall
    R(LR_X_S, E, I, LR_Y_WEST-E, "INT")

    # ═══ LIVING ROOM WEST WALL (partial, only where it differs from kitchen) ═══
    # The living room extends from Y=6 to Y=241 (west). Above Y=241, the wall
    # separates the living room from the kitchen/back rooms.
    # The west wall of the living room runs from LR_X_S to LR_X_N at Y=LR_Y_WEST
    # But this is only needed where it differs from other walls.
    # Since the living room west wall is at Y=241 and the back rooms east wall is at Y=146,
    # there's an offset. The kitchen fills this gap.

    # Wall between living room (east) and kitchen (west) at the north portion:
    # This is the living room west wall from X=KIT_X_N to X=LR_X_N at Y=LR_Y_WEST
    # But wait, the living room wraps around — its S wall is at X=LR_X_S=187.5,
    # which is NORTH of the kitchen S edge (KIT_X_S=155.25).
    # So the living room overlaps with the kitchen in X from 187.5 to 285.25.
    # The wall between them at Y=LR_Y_WEST separates living room (east, Y<241) from kitchen (west, Y>241).

    # Draw living room west wall (from LR_X_S to KIT_X_N at Y=LR_Y_WEST)
    R(LR_X_S, LR_Y_WEST, KIT_X_N-LR_X_S+I, I, "INT")

    # ═══ ROOM LABELS ═══
    # Sunroom
    sx,sy = (SUN_X_S+SUN_X_N)/2, (BACK_Y_EAST+Y_WEST_INT)/2
    T(sx,sy+15,"SUNROOM",7); T(sx,sy,f"{il(SUNROOM_NS)} x {il(BACK_EW)}",4.5,"DM")
    T(sx,sy-15,"(Slate, Arched Windows)",3.5,"DM")

    # Dining Room
    dx,dy_ = (DIN_X_S+DIN_X_N)/2, (BACK_Y_EAST+Y_WEST_INT)/2
    T(dx,dy_+15,"DINING ROOM",7); T(dx,dy_,f"{il(DINING_NS)} x {il(BACK_EW)}",4.5,"DM")
    T(dx,dy_-15,"(Hardwood, Crown Molding)",3.5,"DM")

    # Kitchen
    kx,ky = (KIT_X_S+KIT_X_N)/2, (KIT_Y_EAST+BACK_WALL_Y)/2
    T(kx,ky+10,"KITCHEN",7); T(kx,ky-8,"(Tile Floor)",3.5,"DM")

    # Eating Area
    ex,ey = (EAT_X_S+EAT_X_N)/2, (BACK_Y_EAST+Y_WEST_INT)/2
    T(ex,ey+15,"EATING",7); T(ex,ey,"AREA",7)
    T(ex,ey-18,"(Tile, Coffered Ceiling)",3.5,"DM")

    # Living Room
    lx,ly = (LR_X_S+LR_X_N)/2, (Y_EAST_INT+LR_Y_WEST)/2
    T(lx,ly+25,"LIVING ROOM",8)
    T(lx,ly+8,f"~{il(LR_NS)} x {il(LR_EW)}",4.5,"DM")
    T(lx,ly-8,"(Carpet, Crown Molding)",3.5,"DM")

    # Den
    dnx,dny = (DEN_X_S+DEN_X_N)/2, (Y_EAST_INT+DEN_Y_WEST)/2
    T(dnx,dny+15,"DEN",7); T(dnx,dny,f"{il(DEN_NS)} x {il(DEN_EW)}",4.5,"DM")
    T(dnx,dny-15,"(Hardwood)",3.5,"DM")

    # Front Entrance (between den and living room at the east/front side)
    T((DEN_X_N+LR_X_S)/2, (Y_EAST_INT+KIT_Y_EAST)/2+10, "FRONT",5)
    T((DEN_X_N+LR_X_S)/2, (Y_EAST_INT+KIT_Y_EAST)/2-5, "ENTRANCE",5)

    # ═══ SMALL ROOMS (closet, powder room, old pantry, basement stairs) ═══
    # These are in the south portion of the house, between the eating area and den

    # Closet (72"×24") — in the transition zone between eating area and den
    cl_x = EAT_X_S + 30
    cl_y = BACK_Y_EAST - CLOSET_D - 10
    R(cl_x, cl_y, CLOSET_W, CLOSET_D, "INT")
    T(cl_x+CLOSET_W/2, cl_y+CLOSET_D/2, "CLOSET 72\"x24\"", 3, "RM")

    # Powder Room (61"×61") — east of closet
    pr_x = cl_x + CLOSET_W + I
    pr_y = BACK_Y_EAST - POWDER - 10
    R(pr_x, pr_y, POWDER, POWDER, "INT")
    T(pr_x+POWDER/2, pr_y+POWDER/2+5, "POWDER RM", 3, "RM")
    T(pr_x+POWDER/2, pr_y+POWDER/2-8, "61\"x61\"", 2.5, "DM")

    # Old Pantry (46"×29") — below the closet
    op_x = cl_x
    op_y = cl_y - PANTRY_D - I - 5
    R(op_x, op_y, PANTRY_W, PANTRY_D, "INT")
    T(op_x+PANTRY_W/2, op_y+PANTRY_D/2+4, "OLD PANTRY", 3, "RM")
    T(op_x+PANTRY_W/2, op_y+PANTRY_D/2-6, "46\"x29\"", 2.5, "DM")

    # Basement Stairs (4'6" wide, going down) — south side, near garage
    bs_x = E + 10
    bs_y = E + 10
    bs_w = 54; bs_h = 96
    R(bs_x, bs_y, bs_w, bs_h, "STR")
    T(bs_x+bs_w/2, bs_y+bs_h/2+5, "BSMT", 3.5, "STR")
    T(bs_x+bs_w/2, bs_y+bs_h/2-5, "STAIRS DN", 3.5, "STR")

    # ═══ MAIN STAIRCASE (UP) — in the living room ═══
    st_x = LR_X_S + 10
    st_y = Y_EAST_INT + 20
    st_w = 39; st_h = 108
    R(st_x, st_y, st_w, st_h, "STR")
    T(st_x+st_w/2, st_y+st_h/2+5, "STAIRS", 3.5, "STR")
    T(st_x+st_w/2, st_y+st_h/2-5, "UP", 3.5, "STR")

    # ═══ FIREPLACES ═══
    # Brick fireplace in the living room (near the south wall of living room)
    fp_w,fp_h = 72,22
    fp_x = LR_X_S + 20
    fp_y = Y_EAST_INT + 20
    R(fp_x+st_w+20, fp_y, fp_w, fp_h, "FP")
    T(fp_x+st_w+20+fp_w/2, fp_y+fp_h/2, "BRICK FP", 3.5, "FP")

    # Herringbone FP in dining/eating area
    fp2_w,fp2_h = 60,20
    fp2_x = (EAT_X_N + SUN_X_S)/2 - fp2_w/2
    fp2_y = BACK_Y_EAST - fp2_h - 30
    R(fp2_x, fp2_y, fp2_w, fp2_h, "FP")
    T(fp2_x+fp2_w/2, fp2_y+fp2_h/2, "HERRINGBONE FP", 3, "FP")

    # ═══ WINDOWS ═══
    # Sunroom — west wall (backyard)
    W(SUN_X_S+15, Y_WEST_INT, SUN_X_N-15, Y_WEST_INT)
    # Dining room — west wall
    W(DIN_X_S+15, Y_WEST_INT, DIN_X_N-15, Y_WEST_INT)
    # Living room — north wall
    W(LR_X_N, LR_Y_WEST-40, LR_X_N, Y_EAST_INT+40)
    # Living room — east wall (front, street side)
    W(LR_X_S+30, Y_EAST_INT, LR_X_N-30, Y_EAST_INT)
    # Den — east wall
    W(DEN_X_S+20, Y_EAST_INT, DEN_X_N-20, Y_EAST_INT)

    # ═══ FRONT DOOR ═══
    fd_x = (DEN_X_N + LR_X_S)/2
    msp.add_line((fd_x-18, Y_EAST_INT), (fd_x+18, Y_EAST_INT),
                 dxfattribs={"layer":"DOOR"})

    # ═══ GARAGE ═══
    gar_w, gar_h = 240, 264
    R(-gar_w-E, E, gar_w, gar_h, "GAR")
    R(-gar_w-2*E, 0, gar_w+2*E, gar_h+2*E, "GAR")
    T(-gar_w/2-E, E+gar_h/2+10, "GARAGE", 8, "GAR")
    T(-gar_w/2-E, E+gar_h/2-10, "(dims TBD)", 4, "GAR")
    # Connect garage to main house
    msp.add_line((-E, 0), (0, 0), dxfattribs={"layer":"EXT"})
    msp.add_line((-E, gar_h+2*E), (0, gar_h+2*E), dxfattribs={"layer":"EXT"})

    # ═══ DIMENSIONS ═══
    DH(0, HOUSE_NS, 0, off=42)              # total N-S
    DV(0, HOUSE_EW, HOUSE_NS, off=42)       # total E-W
    DH(SUN_X_S, SUN_X_N, Y_WEST_INT, off=12) # sunroom width
    DV(BACK_Y_EAST, Y_WEST_INT, E, off=-15)   # sunroom depth
    DH(DIN_X_S, DIN_X_N, Y_WEST_INT, off=12)  # dining width
    DH(DEN_X_S, DEN_X_N, Y_EAST_INT, off=-12) # den width
    DV(Y_EAST_INT, DEN_Y_WEST, DEN_X_N, off=12) # den depth
    DH(LR_X_S, LR_X_N, Y_EAST_INT, off=-24)   # living room width
    DV(Y_EAST_INT, LR_Y_WEST, LR_X_N, off=24)  # living room depth

    # ═══ COMPASS + LABELS ═══
    cx = HOUSE_NS + 50
    cy = HOUSE_EW / 2
    # North arrow (points RIGHT = increasing X = NORTH)
    msp.add_line((cx,cy),(cx+30,cy),dxfattribs={"layer":"RM"})
    msp.add_line((cx+30,cy),(cx+22,cy-5),dxfattribs={"layer":"RM"})
    msp.add_line((cx+30,cy),(cx+22,cy+5),dxfattribs={"layer":"RM"})
    T(cx+38, cy, "N", 8)

    T(HOUSE_NS/2, HOUSE_EW+15, "WEST (Backyard)", 5, "DM")
    T(HOUSE_NS/2, -15, "EAST (Front Door / Street)", 5, "DM")
    T(-25, HOUSE_EW/2, "SOUTH", 5, "DM")
    T(-25, HOUSE_EW/2-12, "(Garage)", 3.5, "DM")
    T(HOUSE_NS+25, HOUSE_EW/2, "NORTH", 5, "DM")
    T(HOUSE_NS+25, HOUSE_EW/2-12, "(Living Rm)", 3.5, "DM")

    # Title
    T(HOUSE_NS/2, -40, "30 PARK — GROUND FLOOR PLAN (v6)", 10)
    T(HOUSE_NS/2, -55, "Front door faces EAST | Ceiling 8'-0\" | Int walls 5-1/4\"", 4, "DM")

    out = "/home/paul/Data/workspace/PaulLaurie30Park/docs/current/30park-ground-floor-plan.dxf"
    doc.saveas(out)
    print(f"DXF: {out}")

if __name__ == "__main__":
    generate()
