#!/usr/bin/env python3
"""
30 Park Ground Floor Plan v7 — detailed relationships from user.

COMPASS: Front door = EAST, Backyard = WEST, Living Room = NORTH, Garage = SOUTH
AXES:    Y increases EAST (front), X increases NORTH (living room)
Origin:  (0,0) = South-West exterior corner

KEY RELATIONSHIPS (from user):
- 31'7" = from dining room EAST wall to living room EAST wall
- 11'8"(N-S) x 11'6"(E-W) SPACE between dining and living, directly east of dining
- Kitchen N wall in line with sunroom/dining divider
- Kitchen directly east of sunroom
- Powder room east wall in line with kitchen east wall
- Powder room south of kitchen, directly east of eating area
- Powder room N wall in line with north (open) end of eating area
- 36" hall between powder room east wall and den west wall
- Pantry SE corner = den SW corner
- Hall between pantry west side and closet east side
"""
import ezdxf, math
from ezdxf.enums import TextEntityAlignment

E = 6.0
I = 5.25

# ── room dims (inches) ──
SUN_NS, SUN_EW   = 130, 222   # 10'10" x 18'6"
DIN_NS, DIN_EW   = 140, 222   # 11'8"  x 18'6"
SPACE_NS, SPACE_EW = 140, 138 # 11'8" x 11'6"
LIV_NS, LIV_EW   = 243, 235   # 20'3" x 19'7"
DEN_NS, DEN_EW   = 144, 144   # 12' x 12'
POW             = 61          # 61x61
CLO_NS, CLO_EW   = 72, 24
PAN_NS, PAN_EW   = 46, 29
HALL            = 36
BSMT_NS         = 54

# ── Y axis (East-West): 0=west/back ──
WEST_INT = E                          # 6
DIN_W = WEST_INT                      # dining/sunroom west wall
DIN_E = DIN_W + DIN_EW                # 228  (dining east wall)
SPACE_W = DIN_E + I                   # 233.25
SPACE_E = SPACE_W + SPACE_EW          # 371.25
LIV_W = SPACE_E + I                   # 376.5
LIV_E = LIV_W + LIV_EW                # 611.5  (living east wall = front)
EAST_INT = LIV_E
HOUSE_EW = EAST_INT + E               # 617.5

# kitchen east wall = powder east wall ; align kitchen E-W with the space
KIT_W = SPACE_W                       # 233.25 (east of sunroom)
KIT_E = SPACE_E                       # 371.25
POW_E = KIT_E                         # powder east = kitchen east
POW_W = POW_E - POW                   # 310.25
CLO_W = POW_W                         # closet west = powder west
# eating area: 10'6" E-W, west wall 50" west of sunroom/kitchen divider (KIT_W)
EAT_EW = 126                          # 10'6"
EAT_W = KIT_W - 50                    # 183.25
EAT_E = EAT_W + EAT_EW                # 309.25
# den east wall = living east wall - 48" (4' west of living east)
DEN_E = LIV_E - 48                    # 563.5
DEN_W = DEN_E - DEN_EW                # 419.5

# ── X axis (North-South): 0=south/garage ──
SUN_S = 200.0
SUN_N = SUN_S + SUN_NS                # 330
DIV_S = SUN_N                         # divider between sunroom & dining
DIV_N = DIV_S + I                     # 335.25
DIN_S = DIV_N                         # 335.25
DIN_N = DIN_S + DIN_NS               # 475.25
NORTH_INT = DIN_N                     # 475.25
HOUSE_NS = NORTH_INT + E              # 481.25

KIT_S = SUN_S                         # kitchen S = sunroom S (directly east of sunroom)
KIT_N = SUN_N                         # kitchen N = divider line
POW_N = KIT_S                         # powder N = kitchen S = eating north
POW_S = POW_N - POW                   # 139
EAT_NS = 183                          # 15'3" N-S
EAT_N = KIT_S                         # eating north (open to kitchen)
EAT_S = EAT_N - EAT_NS               # 17
DEN_N = KIT_S                         # den N = kitchen S edge
DEN_S = DEN_N - DEN_NS               # 56
# closet NW corner = powder SW corner (closet directly south of powder)
CLO_N = POW_S                         # 139
CLO_S = CLO_N - CLO_NS               # 67

# space east of dining: same N-S as dining
SPACE_S = DIN_S
SPACE_N = DIN_N

# living room: N wall aligned with dining/space north
LIV_N = DIN_N                         # 475.25
LIV_S = LIV_N - LIV_NS               # 232.25

# basement stairs south of den
BSMT_S = E
BSMT_N = DEN_S                        # up to den south

# pantry: SE corner = den SW corner = (DEN_S, DEN_W)
PAN_S = DEN_S
PAN_N = PAN_S + PAN_NS               # 102
PAN_E = DEN_W                         # 419.5
PAN_W = PAN_E - PAN_EW               # 390.5

# closet east face (west=CLO_W already set = POW_W)
CLO_E = CLO_W + CLO_EW               # 334.25

def il(v):
    f,r = divmod(abs(v),12)
    return f"{int(f)}'-{int(round(r))}\"" if round(r) else f"{int(f)}'-0\""

def generate():
    doc = ezdxf.new("R2010"); msp = doc.modelspace()
    for n,c,w in [("EXT",7,50),("INT",7,35),("DOOR",30,18),("WIN",5,25),
                   ("FP",1,25),("STR",8,13),("FIX",6,13),("DIM",3,13),
                   ("RM",2,13),("DM",3,13),("GAR",9,35)]:
        doc.layers.add(n,color=c,lineweight=w)
    doc.dimstyles.new("D",dxfattribs={"dimtxt":4,"dimasz":3,"dimexe":2,
                                       "dimexo":2,"dimgap":1.5,"dimlfac":1/12})
    FY = HOUSE_EW                      # flip so EAST (front, high Y) is at bottom
    def fy(y): return FY - y
    def R(x,y,w,h,L="INT"):
        msp.add_lwpolyline([(x,fy(y)),(x+w,fy(y)),(x+w,fy(y+h)),(x,fy(y+h))],
                           close=True,dxfattribs={"layer":L})
    def T(x,y,s,h=6,L="RM"):
        msp.add_text(s,height=h,dxfattribs={"layer":L}).set_placement(
            (x,fy(y)),align=TextEntityAlignment.MIDDLE_CENTER)
    def LN(x1,y1,x2,y2,L="RM"):
        msp.add_line((x1,fy(y1)),(x2,fy(y2)),dxfattribs={"layer":L})
    def DH(x1,x2,y,o=18):
        d=msp.add_linear_dim(base=(x1,fy(y)-o),p1=(x1,fy(y)),p2=(x2,fy(y)),
                             dimstyle="D",dxfattribs={"layer":"DIM"}); d.render()
    def DV(y1,y2,x,o=18):
        d=msp.add_linear_dim(base=(x-o,fy(y1)),p1=(x,fy(y1)),p2=(x,fy(y2)),
                             angle=90,dimstyle="D",dxfattribs={"layer":"DIM"}); d.render()

    # rooms as rectangles (note: X=horizontal/N-S, Y=vertical/E-W in DXF space,
    # but we map X->dxf_x and Y->dxf_y so right=North, up=East... we want
    # up=West actually. Let's draw with dxf_x=X (north right), dxf_y=Y (east up).)
    # That puts East at top. We want front door visible; East at top is fine.

    # EXTERIOR
    R(0,0,HOUSE_NS,HOUSE_EW,"EXT")
    R(E,E,HOUSE_NS-2*E,HOUSE_EW-2*E,"EXT")

    # rooms (x=N-S coord, y=E-W coord)
    def room(xs,xn,yw,ye,name,dims,note,big=7):
        R(xs,yw,xn-xs,ye-yw,"INT")
        cx,cy=(xs+xn)/2,(yw+ye)/2
        T(cx,cy+12,name,big);
        if dims: T(cx,cy-2,dims,4.2,"DM")
        if note: T(cx,cy-14,note,3.3,"DM")

    room(SUN_S,SUN_N,DIN_W,DIN_E,"SUNROOM",f"{il(SUN_NS)} x {il(SUN_EW)}","(Slate, Arched Win)")
    room(DIN_S,DIN_N,DIN_W,DIN_E,"DINING ROOM",f"{il(DIN_NS)} x {il(DIN_EW)}","(Hardwood, Crown)")
    room(KIT_S,KIT_N,KIT_W,KIT_E,"KITCHEN","","(Tile)")
    room(DEN_S,DEN_N,DEN_W,DEN_E,"DEN",f"{il(DEN_NS)} x {il(DEN_EW)}","(Hardwood)")

    # PIANO ROOM (open on east side to the living room — no wall there)
    LN(SPACE_S,SPACE_W,SPACE_N,SPACE_W,"INT")   # west wall
    LN(SPACE_S,SPACE_W,SPACE_S,SPACE_E,"INT")   # south wall
    LN(SPACE_N,SPACE_W,SPACE_N,SPACE_E,"INT")   # north wall
    pcx,pcy=(SPACE_S+SPACE_N)/2,(SPACE_W+SPACE_E)/2
    T(pcx,pcy+10,"PIANO ROOM",6); T(pcx,pcy-4,f"{il(SPACE_NS)} x {il(SPACE_EW)}",4,"DM")

    # LIVING ROOM (west wall only south of the piano room; open to piano room)
    LN(LIV_S,LIV_E,LIV_N,LIV_E,"INT")           # east wall (front)
    LN(LIV_S,LIV_W,LIV_S,LIV_E,"INT")           # south wall
    LN(LIV_N,LIV_W,LIV_N,LIV_E,"INT")           # north wall
    LN(LIV_S,LIV_W,SPACE_S,LIV_W,"INT")         # west wall (south of piano room only)
    lcx,lcy=(LIV_S+LIV_N)/2,(LIV_W+LIV_E)/2
    T(lcx,lcy+14,"LIVING ROOM",8); T(lcx,lcy,f"~{il(LIV_NS)} x {il(LIV_EW)}",4.2,"DM")
    T(lcx,lcy-12,"(Carpet, Brick FP)",3.3,"DM")
    R(EAT_S,EAT_W,EAT_N-EAT_S,EAT_E-EAT_W,"INT")
    T((EAT_S+EAT_N)/2,(EAT_W+EAT_E)/2+8,"EATING",6); T((EAT_S+EAT_N)/2,(EAT_W+EAT_E)/2-6,"AREA",6)

    # small rooms
    R(POW_S,POW_W,POW,POW,"INT"); T((POW_S+POW_N)/2,(POW_W+POW_E)/2+3,"POWDER",3); T((POW_S+POW_N)/2,(POW_W+POW_E)/2-6,"61x61",2.5,"DM")
    R(PAN_S,PAN_W,PAN_NS,PAN_EW,"INT"); T((PAN_S+PAN_N)/2,(PAN_W+PAN_E)/2+3,"PANTRY",2.7); T((PAN_S+PAN_N)/2,(PAN_W+PAN_E)/2-5,"46x29",2.3,"DM")
    R(CLO_S,CLO_W,CLO_NS,CLO_EW,"INT"); T((CLO_S+CLO_N)/2,(CLO_W+CLO_E)/2,"CLOSET",2.7); T((CLO_S+CLO_N)/2,(CLO_W+CLO_E)/2-6,"72x24",2.3,"DM")
    R(BSMT_S,DIN_W+20,BSMT_NS,96,"STR"); T(BSMT_S+BSMT_NS/2,DIN_W+20+48,"BSMT DN",3,"STR")

    # main stairs UP — on the EAST wall of the living room, south end
    # 17'0" from windows to stairs, stairs 3'3" wide (N-S), run westward from east wall
    R(LIV_S+8, LIV_E-108, 39, 108, "STR"); T(LIV_S+8+20, LIV_E-54, "UP", 3.5, "STR")

    # fireplace — on the EAST wall of the living room
    R(lcx-36, LIV_E-22, 72, 22, "FP"); T(lcx, LIV_E-11, "BRICK FP", 3, "FP")

    # GARAGE (south of house). East wall in line with living room east outer wall.
    GD = 240                          # garage depth N-S (estimate)
    gar_e = HOUSE_EW                  # garage east = living room east outer wall
    gar_w = gar_e - 264              # ~22' wide E-W (estimate)
    R(-GD-E, gar_w, GD, gar_e-gar_w, "GAR")
    R(-GD-2*E, gar_w-E, GD+2*E, gar_e-gar_w+2*E, "GAR")
    T(-GD/2, (gar_w+gar_e)/2, "GARAGE (dims TBD)", 7, "GAR")

    # dimensions
    DH(0,HOUSE_NS,0,o=40); DV(0,HOUSE_EW,HOUSE_NS,o=40)
    DV(DIN_E,LIV_E,DIN_N+15,o=-30)  # 31'7" dining-east to living-east

    # compass (N points right = +X)
    cx,cy=HOUSE_NS+50,HOUSE_EW/2
    LN(cx,cy,cx+30,cy); LN(cx+30,cy,cx+22,cy+5); LN(cx+30,cy,cx+22,cy-5)
    T(cx+40,cy,"N",8)
    # after flip: EAST (front) is at bottom, WEST (back) at top
    T(HOUSE_NS/2,HOUSE_EW+15,"EAST (Front Door / Street)",5,"DM")
    T(HOUSE_NS/2,-15,"WEST (Backyard)",5,"DM")
    T(-25,HOUSE_EW/2,"SOUTH (Garage)",4,"DM")
    T(HOUSE_NS+30,HOUSE_EW/2+40,"NORTH (Living Rm)",4,"DM")
    T(HOUSE_NS/2,-45,"30 PARK — GROUND FLOOR (v7)",10)

    out="/home/paul/Data/workspace/PaulLaurie30Park/docs/current/30park-ground-floor-plan.dxf"
    doc.saveas(out); print("DXF saved")

if __name__=="__main__":
    generate()
