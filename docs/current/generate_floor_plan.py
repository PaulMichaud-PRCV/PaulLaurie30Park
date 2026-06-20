#!/usr/bin/env python3
"""
30 Park Ground Floor Plan v8 — 3-rectangle structure.

COMPASS: Front door = EAST, Backyard = WEST, Living Room = NORTH, Garage = SOUTH
AXES:    X increases NORTH, Y increases EAST.  Drawing flips Y so EAST is at bottom.

STRUCTURE (3 rectangles; only the garage is a fully contained rectangle):
  NORTH rect : W=sunroom/dining west wall; N=dining/piano/living north wall;
               E=living room + stairs east wall; S=in line with sunroom south wall
  CENTRAL    : W=eating area west wall (50" west of kitchen west wall);
               E=den east wall; joins north rect (N) and garage (S)
  GARAGE     : own rectangle; W=in line with kitchen west wall;
               E=in line with living room east outer wall

KEY DIMS:
  Sunroom 10'10"x18'6" | Dining 11'8"x18'6" | Piano 11'8"x11'6" | Living ~20'3"x19'7"
  Den 12'x12' | Eating 10'6"(E-W) x15'3"(N-S) | Powder 61x61 | Closet 72x24 | Pantry 46x29
  31'7" = dining east wall to living east wall
  Front door: 4' west of den east wall, 130" wide (den north wall to stairs south wall)
  Stairs: double-wide (96") 180-deg turn; west edge = front-door wall line
  Fireplace + stairs on living room EAST wall
"""
import ezdxf, math
from ezdxf.enums import TextEntityAlignment

E = 6.0; I = 5.25

# ── E-W (Y) coordinates : 0 = west/back ──
DIN_W = E                         # 6  sunroom/dining west wall
DIN_E = DIN_W + 222               # 228 dining/sunroom east wall (18'6")
KIT_W = DIN_E + I                 # 233.25 kitchen west wall
KIT_E = KIT_W + 138               # 371.25 (kitchen E-W ~11'6", = piano E-W)
SPACE_W = KIT_W                   # piano room west
SPACE_E = KIT_E                   # 371.25 piano east (open to living)
LIV_W = SPACE_E + I               # 376.5 living west wall
LIV_E = LIV_W + 235               # 611.5 living east wall (19'7") = front/east
EAST_OUT = LIV_E + E              # 617.5

POW_E = KIT_E                     # powder east = kitchen east
POW_W = POW_E - 61                # 310.25
CLO_W = POW_W                     # closet west = powder west
CLO_E = CLO_W + 24                # 334.25
EAT_E = POW_W                     # eating east ~ powder west
EAT_W = KIT_W - 50                # 183.25 (50" west of kitchen west wall)
DEN_E = LIV_E - 48                # 563.5 (4' west of living east)
DEN_W = DEN_E - 144               # 419.5
PAN_E = DEN_W                     # pantry east = den west
PAN_W = PAN_E - 29                # 390.5
OPEN_W = EAT_W                    # open space west = eating area west wall
OPEN_E = KIT_E                    # open space east = kitchen/powder east wall
FRONTDOOR_Y = DEN_E - 48          # 515.5 (front door 4' west of den east)
STAIR_W_Y = FRONTDOOR_Y           # stairs west edge = front-door wall line
STAIR_E_Y = LIV_E                 # stairs east = living east

# ── N-S (X) coordinates : anchor so garage south = 0 ──
GARAGE_D = 240                    # garage depth N-S (estimate)
# Chain: garage_N = eating_S ; eating 183 N-S ; eating_N = kitchen_S = den_N ;
#        den 144 N-S ; entry 130 from den_N to main-stairs-south = SUN_S
# => SUN_S = garage_D + (eating_S->garage gap 0) ... solve below
GARAGE_N = GARAGE_D               # 240 (garage south = 0)
EAT_S = GARAGE_N                  # eating south = garage north (where they overlap)
EAT_N = EAT_S + 183               # 423 eating north (15'3")
# 72" open space extends kitchen south; sits between eating/den-north line and kitchen
OPEN_S = EAT_N                    # 423 (south edge of open space = eating/den/powder north)
OPEN_N = OPEN_S + 72              # 495 (north edge = kitchen south)
KIT_S = OPEN_N                    # 495 kitchen south
DEN_N = EAT_N                     # 423 den north
DEN_S = DEN_N - 144               # 279 den south
# kitchen is directly east of the sunroom -> kitchen south = sunroom south
# entryway = open-space band = 72" (den north to bedroom-stairs south = sunroom south)
SUN_S = KIT_S                     # 495 sunroom south = kitchen south
SUN_N = SUN_S + 130               # 625 sunroom north
KIT_N = SUN_N                     # 683 kitchen north = sun/dining divider line
DIV_S = SUN_N; DIV_N = DIV_S + I  # sun/dining divider
DIN_S = DIV_N                     # 688.25
DIN_N = DIN_S + 140               # 828.25 dining north = house north wall
NORTH_OUT = DIN_N + E

SPACE_S = DIN_S; SPACE_N = DIN_N  # piano N-S = dining N-S (east of dining)
LIV_N = DIN_N                     # living north = north wall
LIV_S = LIV_N - 243               # 585.25 (20'3" N-S)
ENTRY_S = DEN_N                   # 423
ENTRY_N = SUN_S                   # 553 (main stairs south)
POW_N = KIT_S; POW_S = POW_N - 61 # powder (north = kitchen south)
CLO_N = POW_S; CLO_S = CLO_N - 72 # closet (NW corner = powder SW corner)
PAN_S = DEN_S; PAN_N = PAN_S + 46 # pantry (SE corner = den SW corner)

# main stairs (double-wide 180-turn, on living room east wall, south edge = SUN_S)
STAIR_S = SUN_S; STAIR_N = SUN_S + 96
# stairs UP between den (north) and garage (south); landing east wall = den east
UPSTAIR_N = DEN_S                 # 279 (south of den)
UPSTAIR_S = GARAGE_N              # 240 (north of garage)

def il(v):
    f,r = divmod(abs(v),12)
    return f"{int(f)}'-{int(round(r))}\"" if round(r) else f"{int(f)}'-0\""

def generate():
    doc=ezdxf.new("R2010"); msp=doc.modelspace()
    for n,c,w in [("EXT",7,50),("INT",7,35),("RECT",4,18),("DOOR",30,18),
                   ("WIN",5,25),("FP",1,25),("STR",8,13),("DIM",3,13),
                   ("RM",2,13),("DM",3,13),("GAR",9,35)]:
        doc.layers.add(n,color=c,lineweight=w)
    FY=NORTH_OUT  # not used for flip; we flip Y (east-west) below
    # We flip the E-W axis so EAST (front, high Y) appears at the BOTTOM.
    FLIP=EAST_OUT
    def fy(y): return FLIP - y
    def R(x,yw,w,h,L="INT"):   # x=N-S start, yw=E-W(west) start, w=N-S size, h=E-W size
        y1,y2=fy(yw),fy(yw+h)
        msp.add_lwpolyline([(x,y1),(x+w,y1),(x+w,y2),(x,y2)],close=True,
                           dxfattribs={"layer":L})
    def LN(x1,y1,x2,y2,L="INT"):
        msp.add_line((x1,fy(y1)),(x2,fy(y2)),dxfattribs={"layer":L})
    def T(x,y,s,h=6,L="RM"):
        msp.add_text(s,height=h,dxfattribs={"layer":L}).set_placement(
            (x,fy(y)),align=TextEntityAlignment.MIDDLE_CENTER)

    # ── 3 conceptual rectangles (dashed-ish, light) ──
    R(SUN_S, DIN_W, DIN_N-SUN_S, LIV_E-DIN_W, "RECT")           # NORTH rect
    R(DEN_S, EAT_W, SUN_S-DEN_S, DEN_E-EAT_W, "RECT")           # CENTRAL rect
    # GARAGE (contained)
    R(0, KIT_W, GARAGE_D, LIV_E-KIT_W, "GAR")
    R(-E, KIT_W-E, GARAGE_D+E, LIV_E-KIT_W+2*E, "GAR")
    T(GARAGE_D/2,(KIT_W+LIV_E)/2,"GARAGE (dims TBD)",8,"GAR")

    # ── rooms (interior partitions) ──
    def room(xs,xn,yw,ye,name,dims,note,big=7):
        R(xs,yw,xn-xs,ye-yw,"INT")
        cx,cy=(xs+xn)/2,(yw+ye)/2
        T(cx,cy+12,name,big)
        if dims:T(cx,cy-2,dims,4,"DM")
        if note:T(cx,cy-13,note,3.2,"DM")

    room(SUN_S,SUN_N,DIN_W,DIN_E,"SUNROOM","10'-10\" x 18'-6\"","(Slate, Arched Win)")
    room(DIN_S,DIN_N,DIN_W,DIN_E,"DINING ROOM","11'-8\" x 18'-6\"","(Hardwood, Crown)")
    room(KIT_S,KIT_N,KIT_W,KIT_E,"KITCHEN","","(Tile)")
    # open space extending kitchen on the south side (no full walls; open to kitchen)
    LN(OPEN_S,OPEN_W,OPEN_S,OPEN_E)        # south edge
    LN(OPEN_S,OPEN_W,OPEN_N,OPEN_W)        # west edge
    LN(OPEN_S,OPEN_E,OPEN_N,OPEN_E)        # east edge
    T((OPEN_S+OPEN_N)/2,(OPEN_W+OPEN_E)/2,"(open to kitchen)",3,"DM")
    room(DEN_S,DEN_N,DEN_W,DEN_E,"DEN","12'-0\" x 12'-0\"","(Hardwood)")
    room(EAT_S,EAT_N,EAT_W,EAT_E,"EATING AREA","10'-6\" x 15'-3\"","(Tile)")

    # piano room (open east to living room)
    LN(SPACE_S,SPACE_W,SPACE_N,SPACE_W); LN(SPACE_S,SPACE_W,SPACE_S,SPACE_E)
    LN(SPACE_N,SPACE_W,SPACE_N,SPACE_E)
    T((SPACE_S+SPACE_N)/2,(SPACE_W+SPACE_E)/2+8,"PIANO ROOM",6)
    T((SPACE_S+SPACE_N)/2,(SPACE_W+SPACE_E)/2-5,"11'-8\" x 11'-6\"",3.8,"DM")

    # living room (open to piano room on its west, where they adjoin)
    LN(LIV_S,LIV_E,LIV_N,LIV_E)              # east wall (front)
    LN(LIV_S,LIV_W,LIV_S,LIV_E)              # south wall
    LN(LIV_N,LIV_W,LIV_N,LIV_E)              # north wall
    LN(LIV_S,LIV_W,SPACE_S,LIV_W)            # west wall south of piano room
    LN(SPACE_N,LIV_W,LIV_N,LIV_W)            # west wall north of piano room
    T((LIV_S+LIV_N)/2,(LIV_W+LIV_E)/2+14,"LIVING ROOM",8)
    T((LIV_S+LIV_N)/2,(LIV_W+LIV_E)/2,"~20'-3\" x 19'-7\"",4,"DM")
    T((LIV_S+LIV_N)/2,(LIV_W+LIV_E)/2-12,"(Carpet, Brick FP)",3.2,"DM")

    # small rooms
    R(POW_S,POW_W,61,61); T((POW_S+POW_N)/2,(POW_W+POW_E)/2+3,"POWDER",3); T((POW_S+POW_N)/2,(POW_W+POW_E)/2-6,"61x61",2.4,"DM")
    R(CLO_S,CLO_W,72,24); T((CLO_S+CLO_N)/2,(CLO_W+CLO_E)/2+3,"CLOSET",2.6); T((CLO_S+CLO_N)/2,(CLO_W+CLO_E)/2-5,"72x24",2.2,"DM")
    R(PAN_S,PAN_W,46,29); T((PAN_S+PAN_N)/2,(PAN_W+PAN_E)/2+3,"PANTRY",2.6); T((PAN_S+PAN_N)/2,(PAN_W+PAN_E)/2-5,"46x29",2.2,"DM")

    # entry / front door
    T((ENTRY_S+ENTRY_N)/2,(FRONTDOOR_Y+DEN_E)/2,"ENTRY",4)
    LN(ENTRY_S,FRONTDOOR_Y,ENTRY_N,FRONTDOOR_Y,"DOOR")   # front-door wall line

    # LOFT STAIRS between den (north) and garage (south); landing east wall = den east
    R(UPSTAIR_S, DEN_E-90, UPSTAIR_N-UPSTAIR_S, 90, "STR")
    T((UPSTAIR_S+UPSTAIR_N)/2, DEN_E-45, "LOFT STAIRS", 2.6, "STR")

    # main stairs UP — double-wide on living room EAST wall, 180-deg turn
    R(STAIR_S, STAIR_W_Y, STAIR_N-STAIR_S, STAIR_E_Y-STAIR_W_Y, "STR")
    LN((STAIR_S+STAIR_N)/2, STAIR_W_Y, (STAIR_S+STAIR_N)/2, STAIR_E_Y, "STR")  # center wall of U
    T((STAIR_S+STAIR_N)/2,(STAIR_W_Y+STAIR_E_Y)/2,"BEDROOM STAIRS",3,"STR")

    # fireplace on living room east wall
    fcx=(LIV_S+LIV_N)/2
    R(fcx-36, LIV_E-22, 72, 22, "FP"); T(fcx, LIV_E-11, "BRICK FP", 3, "FP")

    # compass + labels
    cx,cy=NORTH_OUT+40,EAST_OUT/2
    LN(cx,cy,cx+30,cy,"RM"); LN(cx+30,cy,cx+22,cy+5,"RM"); LN(cx+30,cy,cx+22,cy-5,"RM")
    T(cx+40,cy,"N",8)
    T(DIN_N/2,EAST_OUT+20,"EAST (Front Door / Street)",5,"DM")
    T(DIN_N/2,-20,"WEST (Backyard)",5,"DM")
    T(-30,EAST_OUT/2,"SOUTH (Garage)",4,"DM")
    T(NORTH_OUT+25,EAST_OUT/2+40,"NORTH (Living Rm)",4,"DM")
    T(DIN_N/2,-50,"30 PARK — GROUND FLOOR (v8)",10)
    T(DIN_N/2,-65,"3-rectangle structure | Front faces EAST | Ceiling 8'-0\"",4,"DM")

    out="/home/paul/Data/workspace/PaulLaurie30Park/docs/current/30park-ground-floor-plan.dxf"
    doc.saveas(out); print("DXF saved")

if __name__=="__main__":
    generate()
