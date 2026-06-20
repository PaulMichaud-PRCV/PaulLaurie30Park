#!/usr/bin/env python3
"""
30 Park - Ground Floor Plan (v5)

COMPASS ORIENTATION:
- Front door faces EAST (street)
- Back of house faces WEST (backyard)
- Living Room is on the NORTH side
- Garage is on the SOUTH side

DXF ORIENTATION (for conventional floor plan reading):
- X axis = East-West (X increases EAST, toward front door/street)
- Y axis = North-South (Y increases NORTH, toward living room)
- Origin (0,0) = SW exterior corner (garage side, back of house)

VERIFIED MEASUREMENTS:
- Sunroom: 10'10" wide (N-S) × 18'6" deep (E-W)
- Dining Room: 11'8" wide (N-S) × 18'6" deep (E-W)
- Den: 12' × 12'
- Powder Room: 61" × 61"
- Back Closet (bifold): 72" wide × 24" deep
- Old Pantry: 46" wide × 29" deep
- Basement stairs: ~4'6" wide
- Living room front: 17'0" windows-to-stairs, stairs 3'3" wide
- Living room depth (left side): 19'7"
- N-S fireplace wall: 31'7"
- Door dining→den: 45.5" + ~50" opening + 44.25"
- Total depth (E-W): 31'2" outside wall to back
- Interior walls: 5.25" | Exterior walls: 6" | Ceiling: 96"

LAYOUT (from OmniGraffle + user corrections):

  WEST (backyard)                              EAST (street/front door)
  ┌──────────┬──────────┬──────────────────────┬─────────────────────────┐
  │          │          │                      │                         │ N
  │ Sun Room │Dining Rm │     KITCHEN          │                         │ O
  │10'10"×   │11'8"×    │  (east of sun/din,   │     LIVING ROOM         │ R
  │  18'6"   │ 18'6"    │   N wall aligns with │  (fireplace, stairs UP) │ T
  │          │          │   sun/din divider)    │                         │ H
  ├──────────┴──────────┤......................├─────────────────────────┤
  │                     │                      │                         │
  │   EATING AREA       │  (open to kitchen,   │   FRONT ENTRANCE        │
  │                     │   no wall between)   │   (front door→EAST)     │
  │  ┌Closet┬─Powder┐  │                      │                         │
  │  │72×24 │Rm61×61│  │                      │   Stairs UP             │
  │  ├──────┴───────┘  │                      │                         │
  │  │OldPantry 46×29  │                      │                         │
  │  ├─────┬────────────┤                      │                         │
  │  │Bsmt │   Den      │                      │                         │ S
  │  │Strs │  12'×12'   │                      │                         │ O
  │  │ DN  │            │                      │                         │ U
  │  │     │            │                      │    Fireplace            │ T
  ├──┤     │            │                      │                         │ H
  │GA│     │            │                      │                         │
  │RA│     │            │                      │                         │
  │GE│     │            │                      │                         │
  └──┴─────┴────────────┴──────────────────────┴─────────────────────────┘
"""

import ezdxf
from ezdxf.enums import TextEntityAlignment
import math

EXT = 6.0
INT = 5.25

# === KEY DIMENSIONS ===
# E-W depth (total exterior): 31'2" = 374"
HOUSE_EW = 374.0

# Back rooms E-W depth: 18'6" = 222" (sunroom and dining room)
BACK_ROOM_EW = 222.0

# Room widths (N-S)
SUNROOM_NS = 130.0    # 10'10"
DINING_NS = 140.0     # 11'8"
DEN_NS = 144.0        # 12' (N-S)
DEN_EW = 144.0        # 12' (E-W)
POWDER_NS = 61.0
POWDER_EW = 61.0
CLOSET_NS = 72.0      # bifold closet
CLOSET_EW = 24.0
PANTRY_NS = 46.0      # Old Pantry
PANTRY_EW = 29.0
BSMT_STAIR_NS = 54.0  # 4'6"

# Living room
LR_FRONT_TO_STAIRS = 204.0  # 17'0" from windows to stairs
STAIR_NS = 39.0             # 3'3" stairs wide (N-S)

# Kitchen: N wall aligns with sunroom/dining divider wall
# Kitchen: S edge aligns with den N wall and powder room N wall

# === COORDINATE SYSTEM ===
# X = East (increases toward front door / street)
# Y = North (increases toward living room)
# Origin (0,0) = SW exterior corner

# --- Y coordinates (North-South) ---
# The house N-S width: sunroom + wall + dining room + more on the south
# Sunroom is on the NORTH side of the back, dining room south of it
# Actually from OmniGraffle: sunroom is to the LEFT of dining room in the diagram
# which (with front=east, north=top) means sunroom is NORTH of dining room

# Back section N-S (from south): Dining Room (south) | wall | Sunroom (north)
# Then the kitchen is EAST of them, with N wall aligned to the sun/din divider

# Let me set Y coordinates from south to north:
# Y=0: south exterior wall (garage side)

# The garage is on the SOUTH side, the living room on the NORTH
# From south to north: garage area / den / eating area ... sunroom / living room

# I need to figure out the total N-S width of the house.
# From the OmniGraffle, the rooms from south to north at the back:
# Dining Room (11'8" = 140") at the south, Sunroom (10'10" = 130") at the north
# Total back section: 140 + INT + 130 = 275.25"

# At the front, from south to north:
# Den (12' = 144") ... front entrance ... Living Room (17'0" + 3'3" = 20'3" = 243")
# Total front: 144 + walls + entrance + walls + 243

# The kitchen N wall aligns with the sunroom/dining divider
# The kitchen S edge aligns with the den N wall

# So the sunroom/dining divider Y position = den N wall Y position
# Dining room (south): from Y_south to Y_divider
# Den (south): from Y_den_south to Y_den_north = Y_divider

# If dining room N-S = 140" and den N-S = 144":
# Dining starts at Y_dining_south, ends at Y_divider
# Den starts at Y_den_south, ends at Y_divider
# So Y_dining_south = Y_divider - 140
# Y_den_south = Y_divider - 144

# The den extends 4" further south than the dining room.
# The garage is further south.

# Let me set Y_divider first. Everything is relative to this.
# Sunroom: from Y_divider to Y_divider + INT + 130 = Y_sunroom_north
# Living room: from Y_divider (or wherever) to Y_north

# Actually, the kitchen S edge (= den N wall = powder room N wall) is at Y_divider
# The kitchen N wall is at Y_divider + INT + DINING_NS ... wait no.
# The kitchen N wall aligns with the sunroom/dining DIVIDER wall.
# The sunroom/dining divider is between dining room (south) and sunroom (north).
# So the kitchen N wall Y = same as sunroom S wall Y = Y_divider + some offset

# Let me redefine:
# The wall between dining room and sunroom is at Y = SUN_DIN_WALL_Y
# This wall runs E-W
# South of it: Dining Room (11'8" going south)
# North of it: Sunroom (10'10" going north)
# Kitchen N wall aligns with this wall

# Kitchen S edge aligns with den N wall
# Let me call this Y = KIT_S_Y

# Between KIT_S_Y and SUN_DIN_WALL_Y is the kitchen N-S height
# This should equal the dining room N-S = 140" (since kitchen spans from den top to din/sun divider)
# Kitchen N-S = SUN_DIN_WALL_Y - KIT_S_Y

# The dining room spans from KIT_S_Y to SUN_DIN_WALL_Y (same as kitchen N-S span):
# Wait, no. The dining room is at the BACK (west). Its N-S = 140".
# Dining room S wall = SUN_DIN_WALL_Y - 140 - INT ...

# Let me think differently. The dining room south wall and the den north wall are NOT necessarily
# at the same Y. The alignment is:
# - Kitchen N wall = Sunroom/Dining divider wall (same Y)
# - Kitchen S edge = Den N wall = Powder Room N wall (same Y)

# The dining room occupies: from its S wall to the sunroom/dining divider
# Dining room N-S = 11'8" = 140"
# So dining room S wall = SUN_DIN_WALL_S - 140 (where SUN_DIN_WALL_S = south face of divider)

# The den N wall = kitchen S edge. If this equals the dining room S wall:
# Kitchen S Y = Dining room S wall Y = SUN_DIN_WALL_S - 140

# Kitchen N-S = SUN_DIN_WALL_S - (SUN_DIN_WALL_S - 140) = 140"
# So the kitchen is 140" N-S, same as the dining room. Makes sense!

# Now from south to north at the back:
# Y=dining_S_wall: bottom of dining room
# Y=dining_S_wall + 140: top of dining room = south face of sun/din divider wall
# Y=dining_S_wall + 140 + INT: north face of divider = south wall of sunroom
# Y=dining_S_wall + 140 + INT + 130: north wall of sunroom

# Kitchen S edge = dining_S_wall (same Y)
# Kitchen N wall = south face of divider = dining_S_wall + 140

# Now, the den N wall also = dining_S_wall (= kitchen S edge)
# Den is 144" (12') N-S, going SOUTH from dining_S_wall
# Den S wall = dining_S_wall - 144

# The garage is further south.

# Living room is on the NORTH side:
# Living room extends from somewhere north of the sunroom or at the same level

# From the OmniGraffle, the living room extends from roughly the den/eating area level
# all the way north. Its N wall is the north exterior wall.

# Let me set coordinates:
# Let's put the dining room S wall / kitchen S edge / den N wall at a reference point.

# Y coordinates (from south):
GARAGE_D = 264.0  # garage depth E-W (estimated)
GARAGE_NS = 240.0  # garage width N-S (estimated)

# Den S wall position - den extends 144" south from the kitchen S edge
# Kitchen S edge = Den N wall
# Let's set Y=0 at the south exterior wall

# From south to north:
# Y=0: south exterior wall
# Y=EXT: south interior wall
# ... garage and den are in this zone ...
# Y=DEN_N: den north wall = kitchen south edge = dining room south wall

# Den is 144" N-S. Den south wall at some Y, den north at DEN_N = den_south + 144
# Below the den (further south) is the garage area

# Let me figure out total house N-S width from what I know:
# South to north: ... den (144") ... dining room (140") + wall + sunroom (130") ... living room ...
# The living room extends from the front entrance area northward.

# From the OmniGraffle, the living room north edge extends past the sunroom north edge.
# The sunroom and dining room are in the NW corner of the house.

# Total N-S: needs to accommodate:
# - Den (144")
# - Some space south of den (garage connection, basement stairs)
# - Dining room (140") above the den
# - Sunroom (130") above dining room
# - Living room (extends from entrance area past sunroom to north wall)

# At the front (east), the living room spans: 17'0" + 3'3" = 20'3" = 243" N-S
# This likely goes from south of the sunroom/dining divider all the way to the north wall

# Let me set things up:
# DEN_N = kitchen S edge = dining room S wall
# I'll place this at a Y that makes sense.

# The garage extends from the south exterior wall. Let's say the den starts
# above the garage area. There might be a wall between the garage and the den.

# For simplicity, I'll put:
# - Garage at the far south (Y=0 to some height)
# - Den above the garage: DEN_S to DEN_N = DEN_S + 144
# - Basement stairs next to den (same Y range)
# - Kitchen S edge = DEN_N
# - Dining room: DEN_N to DEN_N + 140
# - Divider wall: DEN_N + 140 to DEN_N + 140 + INT
# - Sunroom: DEN_N + 140 + INT to DEN_N + 140 + INT + 130
# - Living room extends from south of the divider to the north wall

# The den S wall might be at the garage N wall level.
# Let me estimate the south exterior wall position.

# If den bottom = garage area top:
# Garage N wall (interior) at Y = garage_height
# Den S wall at Y = garage_height + some_gap_or_wall

# For now, let me place den S wall at Y = EXT (right at the south interior wall)
# This means the garage is NOT within the main house rectangle but attached to the south.

# Actually, from the OmniGraffle, the garage overlaps with the den/basement stairs Y range.
# The garage is to the WEST, and the den is to the EAST at the same Y level.
# The garage and den share the same Y band but different X positions.

# So the Y layout at the front-south portion:
# Basement stairs + Den are at the same Y as part of the garage

# Let me define DEN_S:
# I'll place the den so that DEN_N aligns with the dining room S wall
# DEN_S = DEN_N - 144

# And I need DEN_S > EXT (inside the south wall)
# I'll figure out the total N-S from the room stacking.

# From S to N in the back (west) section:
# ... some space ... then Dining Room (140") then wall (5.25") then Sunroom (130")
# Plus the living room extends north of the sunroom

# The living room N-S = 243" (from 17'0" + 3'3")
# If the living room S edge is at the same Y as the den S edge (both face the south/entrance),
# and the living room extends 243" north:
# LR_N = DEN_S + 243

# And sunroom N wall = DEN_N + 140 + INT + 130 = DEN_S + 144 + 140 + INT + 130 = DEN_S + 419.25

# For the living room to extend past the sunroom:
# LR_N = DEN_S + 243 vs Sunroom_N = DEN_S + 419.25
# 243 < 419.25, so living room is SHORTER than the back rooms stacking!
# This means the sunroom extends further north than the living room.

# But from the OmniGraffle, the living room appears to extend PAST the sunroom to the north.
# So maybe the living room's S edge is further south than the den.

# OR: the 243" (20'3") living room measurement is the E-W dimension (not N-S).
# The user said "the wall along the front of the living room" is 17'0" from windows to stairs.
# "The front of the living room" - the front faces EAST. So this wall runs N-S (along the east-facing front).
# 17'0" N-S from windows to stairs + 3'3" stairs = 20'3" N-S total for the living room front wall!

# So the living room is 20'3" = 243" in the N-S direction. That's its N-S span at the front (east wall).

# And 19'7" = 235" is the living room E-W depth on one side.

# So: Living Room is 243" (N-S, ~20'3") × 235" (E-W, ~19'7")

# Now: Living Room N-S = 243". Back rooms stacking = 140 + 5.25 + 130 = 275.25"
# The living room is SHORTER (N-S) than the back rooms.

# From the OmniGraffle, the living room N wall appears to be roughly at the same Y as
# somewhere between the sunroom N wall and slightly above the sunroom/dining divider.

# The key constraint: the living room is at the NORTH side. So:
# LR_N = north interior wall of house
# LR_S = LR_N - 243

# And the sunroom N wall = DEN_N + 140 + INT + 130

# For the living room to be on the north side:
# LR_N = max of (sunroom_N, LR_S + 243)

# If sunroom_N > LR_N, the sunroom extends past the living room to the north,
# which contradicts "living room is on the north side."

# So LR_N >= sunroom_N:
# LR_N >= DEN_N + 140 + INT + 130 = DEN_N + 275.25
# And LR_N = LR_S + 243

# If LR_S = DEN_S (both start from the same south edge near the entrance):
# LR_N = DEN_S + 243 = DEN_N - 144 + 243 = DEN_N + 99

# For LR_N >= DEN_N + 275.25:
# DEN_N + 99 >= DEN_N + 275.25
# 99 >= 275.25 -- FALSE!

# So the living room S edge must be further SOUTH than the den S edge:
# LR_S + 243 >= DEN_N + 275.25
# LR_S >= DEN_N + 275.25 - 243 = DEN_N + 32.25

# But LR_S should be south of DEN_N. DEN_N + 32.25 means LR_S is NORTH of DEN_N!
# That means the living room starts 32.25" north of the den top, which makes no sense
# if they share the front entrance between them.

# I think the issue is that the living room N-S (243") is measured differently.
# Or the back rooms don't all stack from the same baseline.

# Let me reconsider: maybe the dining room and sunroom share their N-S dimension
# differently. The sunroom is 10'10" and the dining room is 11'8", but they might not
# be stacked N-S. From the OmniGraffle, they appear to be SIDE BY SIDE (same Y range),
# not stacked. Let me re-examine.

# OmniGraffle SVG: Sun Room at (1717, 193, 476×432) and Dining Room at (2193, 193, 476×432)
# They are at the SAME Y (193) and same height (432). So they are side by side N-S,
# NOT stacked! They share the SAME back (west) wall and front wall.

# The "wall separating sunroom and dining room" is a N-S wall between them, not E-W!

# So: Sunroom (10'10") and Dining Room (11'8") are SIDE BY SIDE:
# Total N-S at the back = 10'10" + wall + 11'8" = 130 + 5.25 + 140 = 275.25"
# Sunroom is to the NORTH, Dining Room to the SOUTH
# The divider between them is a N-S wall (running E-W in the house, but separating them N-S)

# Wait, that's wrong too. A wall "separating" two rooms that are side by side (N-S)
# would run E-W (east-west), not N-S.

# Let me re-read: "north wall of the kitchen is in line with the wall separating the
# sun-room and the dining room"
# The wall separating sunroom from dining room runs E-W (since they're side by side N-S)
# The kitchen's N wall also runs E-W
# These are at the same Y position

# So: wall between sunroom (north) and dining room (south) is at Y = some value
# Kitchen N wall is at the same Y
# Kitchen S edge is at the same Y as den N wall

# This means:
# From S to N at the back: Dining Room (140" N-S) | E-W wall | Sunroom (130" N-S)
# From S to N at the kitchen level: (den/entrance stuff) | Kitchen (same height as dining room, 140")

# Total back N-S = 140 + INT + 130 = 275.25"
# = Dining room (south) + wall + Sunroom (north)

# Kitchen N wall Y = Dining room N wall Y = wall between din/sun
# Kitchen S edge Y = Dining room S wall Y = Den N wall Y

# Kitchen N-S height = Dining room N-S = 140"

# Living room on the north side: spans from somewhere south to the north exterior wall
# North exterior N-S = EXT + 130 (sunroom) + INT + 140 (dining) + EXT = at minimum
# Total minimum N-S = 275.25 + 12 = 287.25" ≈ 23'11"

# But living room is 243" N-S and needs to extend to the north wall.
# If total N-S = 287.25", and LR spans the north 243":
# LR_S = 287.25 - 6 - 243 = 38.25" from south exterior
# DEN_N = (287.25 - 6 - 130 - INT - 140) + ...

# Hmm, let me just set up coordinates directly.

# Y=0: south exterior wall
# Y=EXT (6): south interior wall
# ...den starts here...
# Y=DEN_S: den south interior wall
# Y=DEN_S + DEN_NS = DEN_N: den north wall = kitchen S edge = dining room S wall
# Y=DEN_N + DINING_NS = DIN_N: dining room N wall = sun/din divider S face
# Y=DIN_N + INT = SUN_S: sunroom S wall
# Y=SUN_S + SUNROOM_NS = SUN_N: sunroom N wall
# Y=SUN_N + EXT: north exterior wall (if sunroom goes to the edge)

# But living room is to the NORTH and must reach the north wall.
# LR_N = north interior = SUN_N (if sunroom defines the north extent)
# LR_S = LR_N - 243 = SUN_N - 243

# SUN_N = DEN_S + DEN_NS + DINING_NS + INT + SUNROOM_NS
#        = DEN_S + 144 + 140 + 5.25 + 130 = DEN_S + 419.25

# LR_S = DEN_S + 419.25 - 243 = DEN_S + 176.25

# DEN_S should be at least EXT = 6.
# LR_S = 6 + 176.25 = 182.25" from south exterior

# So the living room starts at Y=182.25, which is above the den (DEN_N = 6 + 144 = 150).
# The living room S wall is 32.25" ABOVE the den N wall. There's a gap between the den
# top and the living room bottom. This is the FRONT ENTRANCE area (32.25" ≈ 2'8").

# Total N-S = SUN_N + EXT = 6 + 419.25 + 6 = 431.25" ≈ 35'11"

# Let me set this up:
DEN_S = EXT                          # 6" (against south interior wall)
DEN_N = DEN_S + DEN_NS               # 150"
DIN_S = DEN_N                         # 150" (dining room S wall = den N wall = kitchen S edge)
DIN_N = DIN_S + DINING_NS            # 290" (dining room N wall)
SUN_DIN_WALL_S = DIN_N               # 290" (south face of E-W divider wall)
SUN_DIN_WALL_N = SUN_DIN_WALL_S + INT # 295.25"
SUN_S = SUN_DIN_WALL_N               # 295.25" (sunroom S wall)
SUN_N = SUN_S + SUNROOM_NS           # 425.25" (sunroom N wall)

HOUSE_NS = SUN_N + EXT               # 431.25" ≈ 36'

# Living room
LR_N = SUN_N                         # 425.25" (north interior wall)
LR_S = LR_N - (LR_FRONT_TO_STAIRS + STAIR_NS)  # 425.25 - 243 = 182.25"
LR_EW = LR_FRONT_TO_STAIRS  # Approximate E-W depth (will use 19'7" = 235 on one side)

# Front entrance is between den top (150") and living room bottom (182.25")
ENTRANCE_S = DEN_N                    # 150"
ENTRANCE_N = LR_S                     # 182.25"
ENTRANCE_NS = ENTRANCE_N - ENTRANCE_S # 32.25" ≈ 2'8"

# === X coordinates (East-West) ===
# X increases EAST (toward front door)
# Back rooms (sunroom, dining room) are at the WEST (low X)
# Kitchen, entrance, living room are to the EAST (high X)
# Front door is at the EAST exterior wall

# X=0: west exterior wall (back of house)
# Back rooms E-W depth = 18'6" = 222"
# X=EXT: west interior wall
# X=EXT + BACK_ROOM_EW = 228" (east wall of back rooms)
# Then wall, then kitchen, then more...

BACK_E = EXT + BACK_ROOM_EW          # 228" (east interior face of back rooms)
BACK_WALL_E = BACK_E + INT           # 233.25" (east face of wall between back rooms and kitchen)

# Kitchen is EAST of the back rooms
# Kitchen E-W depth: need to determine
# Total house E-W = 31'2" = 374" (exterior)
# From west: EXT(6) + back_rooms(222) + wall(5.25) + kitchen_EW + ... + EXT(6) = 374
# kitchen_EW + remaining = 374 - 6 - 222 - 5.25 - 6 = 134.75"

# The kitchen and living room share the east portion of the house
# Living room E-W depth = 19'7" = 235" (on one side)
# The living room extends from the front door (east wall) 235" westward

HOUSE_EW_ACTUAL = HOUSE_EW  # 374" total exterior E-W
EAST_INT = HOUSE_EW_ACTUAL - EXT  # 368" (east interior wall = front door wall)
LR_W = EAST_INT - 235.0    # 133" (living room west wall, from front)

# Kitchen is from BACK_WALL_E to some X east
# The kitchen east wall is likely at the same X as the living room west wall
# or the kitchen opens into the eating area / entrance
# For now: kitchen east wall = living room west wall
KIT_E = LR_W                         # 133"
KIT_EW = KIT_E - BACK_WALL_E         # 133 - 233.25 = NEGATIVE!

# Problem: LR_W (133") < BACK_WALL_E (233.25")
# This means the living room extends PAST the back rooms into the back area
# The living room is deeper (E-W) than the remaining space east of the back rooms

# This makes sense if the living room extends westward alongside the back rooms.
# The back rooms are in the NW corner, and the living room wraps around to the west.

# Let me reconsider the X layout:
# The back rooms (sunroom + dining room) are only 222" deep E-W
# but the total house is 374" deep E-W
# The remaining 374 - 222 - 12(ext walls) - 5.25(wall) = 134.75" is the east portion

# The living room is 235" E-W deep, which means it extends from the east wall (X=368)
# westward to X=368-235=133". This is 133" from the west exterior wall.
# The back rooms extend from X=6 to X=228. So the living room overlaps with
# the back rooms from X=133 to X=228 = 95" of overlap.

# In this overlap zone, the living room is to the NORTH of the sunroom,
# or the living room extends the full depth and the sunroom/dining room
# are carved out of the NW corner.

# I think the correct interpretation is:
# The living room spans the FULL north side of the house
# The sunroom and dining room are in the SW and middle-west area
# The kitchen is between the back rooms and the front entrance
# The eating area is south of the kitchen

# Let me redefine the X layout:

# The house is 374" E-W (exterior)
# Living room W wall is at X = EAST_INT - 235 = 368 - 235 = 133"
# This wall runs N-S. The living room is to the EAST of X=133.

# The N-S fireplace wall is 31'7" = 379" long. Hmm, 379 > 374 (house depth).
# Maybe 31'7" is measured from the south wall. Let me not worry about reconciling
# every measurement right now and focus on the layout.

# For the main house width, the back rooms from south to north = 275.25"
# Plus the living room which extends from its S edge (182.25") to the N wall (425.25")
# = 243" N-S

# But the living room might extend further south. Looking at the OmniGraffle,
# the living room and the main staircase extend quite far south.

# Let me just define the rooms by position and draw them.

# REVISED APPROACH: Define room corners explicitly

# --- Back rooms (WEST side of house) ---
# Sunroom: NW corner of back area
sun_x1 = EXT                    # west
sun_x2 = EXT + BACK_ROOM_EW     # east (228")
sun_y1 = SUN_S                   # south (295.25")
sun_y2 = SUN_N                   # north (425.25")

# Dining Room: SW corner of back area
din_x1 = EXT                    # west
din_x2 = EXT + BACK_ROOM_EW     # east (228")
din_y1 = DIN_S                   # south (150")
din_y2 = DIN_N                   # north (290")

# Kitchen: EAST of back rooms, between the sun/din divider and den N wall
kit_x1 = BACK_WALL_E            # west (233.25")
kit_x2 = EAST_INT               # east (368") -- extends to east wall? or less
kit_y1 = DIN_S                   # south = den N wall (150")
kit_y2 = DIN_N                   # north = dining room N wall (290")
# Actually kitchen probably doesn't extend all the way to the east wall
# The front entrance and living room are also at this X range
# Kitchen E wall might stop where the entrance/living room starts
# For now, let kit_x2 = about 300" (estimate, roughly half the remaining space)
kit_x2 = 310.0  # estimate

# Eating Area: SOUTH of kitchen, EAST of dining room
eat_x1 = BACK_WALL_E            # west (233.25")
eat_x2 = kit_x2                  # east = same as kitchen
eat_y1 = EXT                     # south = near south wall
eat_y2 = DIN_S                   # north = den N wall / kitchen S edge (150")

# Living Room: NORTH side, from front entrance east to east wall
lr_x1 = LR_W                    # west (133")
lr_x2 = EAST_INT                # east (368")
lr_y1 = LR_S                    # south (182.25")
lr_y2 = LR_N                    # north (425.25")

# Den: south area, west of entrance
den_x1 = BACK_WALL_E            # west (233.25") - east of back rooms
den_x2 = BACK_WALL_E + DEN_EW   # east (377.25")
den_y1 = DEN_S                   # south (6")
den_y2 = DEN_N                   # north (150")

# Hmm den_x2 = 377.25 but EAST_INT = 368. So den extends past the east wall!
# Den is 12' = 144" E-W, but only 134.75" is available east of the back rooms.
# This means the den extends into the back rooms area, OR
# the den is positioned differently.

# Let me reconsider. Maybe the den is NOT east of the back rooms.
# From the OmniGraffle, the den is at x=872 in SVG, while the back rooms
# start at x=1717. The den is to the LEFT (south/west) of the back rooms in the OmniGraffle.

# With the corrected compass (east = front, north = living room side):
# OmniGraffle LEFT = south/garage side
# OmniGraffle RIGHT = north/living room side
# OmniGraffle TOP = west/backyard
# OmniGraffle BOTTOM = east/front door

# So the den (OmniGraffle x=872-1348) is to the SOUTH (lower Y) of the kitchen and back rooms.
# The den is at the same Y as the basement stairs and garage (south side).
# The den E-W position: OmniGraffle y=1143-1575, which is in the EASTERN (front) half.

# OK so the den is:
# - On the SOUTH side (low Y, between garage and dining room)
# - In the EASTERN half (high X, toward front door)

# Let me reconsider the den position:
# Den E-W: from X = some position to X + 144"
# Den N-S: from Y = some position to Y + 144"
# Den is below (south of) the dining room and kitchen

# If den is in the SE corner of the south portion:
den_x1 = EAST_INT - DEN_EW      # 368 - 144 = 224"
den_x2 = EAST_INT               # 368"
den_y1 = DEN_S                   # 6"
den_y2 = DEN_N                   # 150"

# This puts the den in the front-south area. The east wall of the den is the east exterior wall
# (the front door wall). This makes sense - the den has a window on the front (east) wall.

# The eating area, closet, powder room, old pantry, basement stairs are all
# between the garage (far south-west) and the den (south-east):
eat_x1 = BACK_WALL_E            # 233.25"
eat_x2 = den_x1                  # 224" ... wait, 233 > 224. Problem!

# BACK_WALL_E = 233.25 but den_x1 = 224. The den starts WEST of the back room east wall.
# This means there's overlap: the den extends into the back-rooms X range.

# I think the issue is that the back rooms and den are at DIFFERENT Y positions
# and the den can overlap the same X range as the back rooms (since they don't
# overlap in Y, just in X).

# So vertically:
# Back rooms: Y = 150 to 425.25 (dining room + sunroom)
# Den: Y = 6 to 150
# They don't overlap in Y, so they CAN overlap in X.

# The eating area is between the back rooms and the den, or to the side.
# From the OmniGraffle, the eating area is to the WEST of the kitchen and
# below the back rooms.

# Let me reposition:
# Eating area: west of the kitchen, south of the back rooms
eat_x1 = EXT                    # 6" (against west wall)
eat_x2 = BACK_WALL_E            # 233.25" (east = back room east wall)
eat_y1 = EXT                    # 6" (south)
eat_y2 = DIN_S                  # 150" (north = dining room S / den N)

# Den is to the EAST of the eating area:
den_x1 = eat_x2                 # 233.25" -- right after the eating area wall
# But den is 144" wide: den_x2 = 233.25 + 144 = 377.25 > 368 = EAST_INT!
# Still too wide.

# Maybe there's no wall between eating area and den, and the den starts
# within the eating area zone. Or the den is simply against the east wall:
den_x2 = EAST_INT               # 368"
den_x1 = den_x2 - DEN_EW        # 368 - 144 = 224"

# And the eating area is from X=6 to X=224 (= den_x1), Y=6 to Y=150
eat_x2 = den_x1                 # 224"

# Kitchen: east of back rooms, north of den
kit_x1 = BACK_WALL_E            # 233.25"
kit_x2 = EAST_INT               # 368" (or to the living room west wall)
kit_y1 = DIN_S                   # 150" (= den top = dining room bottom)
kit_y2 = DIN_N                   # 290" (= dining room top = sun/din divider)

# Closet, powder room, old pantry: between eating area and kitchen
# These are small rooms in the transition zone

# Closet (72"×24"):
cl_x1 = eat_x1 + 30             # slightly east of eating area west wall
cl_x2 = cl_x1 + CLOSET_NS       # 72" wide (in the E-W direction? or N-S?)
# The closet is 72" wide × 24" deep. Need to determine orientation.
# From OmniGraffle, closet width runs N-S (it's wider than deep).
# So: 72" in N-S direction, 24" in E-W direction.
cl_y2 = DIN_S                   # north wall aligns with kitchen S / den N (150")
cl_y1 = cl_y2 - CLOSET_NS       # 150 - 72 = 78"
cl_x1 = eat_x1 + 40
cl_x2 = cl_x1 + CLOSET_EW       # 24" deep E-W

# Powder room (61"×61"):
pr_x1 = cl_x2 + INT             # east of closet + wall
pr_x2 = pr_x1 + POWDER_EW       # 61" E-W
pr_y2 = DIN_S                   # 150" (north wall = kitchen S = den N)
pr_y1 = pr_y2 - POWDER_NS       # 150 - 61 = 89"

# Old Pantry (46"×29"):
op_y2 = cl_y1                   # above den, below closet (roughly)
op_y1 = op_y2 - PANTRY_NS       # 46" N-S
op_x1 = cl_x1
op_x2 = op_x1 + PANTRY_EW       # 29" E-W

# Basement stairs: south of closet area
bs_y2 = op_y1
bs_y1 = EXT
bs_x1 = eat_x1 + 10
bs_x2 = bs_x1 + BSMT_STAIR_NS  # 54" wide

# Garage: far south-west
gar_x1 = -GARAGE_NS - EXT       # extends west/south beyond main house
gar_x2 = -EXT
gar_y1 = EXT
gar_y2 = EXT + GARAGE_D

# Actually, garage is on SOUTH side. Let me put it below Y=0:
gar_y1 = -GARAGE_NS - EXT
gar_y2 = -EXT
gar_x1 = EXT
gar_x2 = EXT + GARAGE_D

# Hmm, this is getting complicated with the garage position.
# Let me just place the garage as a separate rectangle to the south.
gar_x1 = EXT
gar_x2 = EXT + 180  # estimated
gar_y1 = -GARAGE_NS
gar_y2 = 0

# Main staircase (UP) in the living room
stair_x = EAST_INT - 40         # near the east wall
stair_y1 = LR_S + 20            # starts near the south end of living room
stair_y2 = stair_y1 + 108       # ~9' run

# Fireplace in living room (near south wall)
fp_x = (lr_x1 + lr_x2) / 2
fp_y = LR_S + 10


def il(v):
    f = int(abs(v)) // 12
    r = abs(v) - f * 12
    if r < 0.1: return f"{f}'-0\""
    if abs(r - round(r)) < 0.1: return f"{f}'-{int(round(r))}\""
    return f"{f}'-{r:.0f}\""


def dim_h(msp, x1, x2, y, off=18):
    d = msp.add_linear_dim(base=(x1, y-off), p1=(x1,y), p2=(x2,y),
                            dimstyle="P30", dxfattribs={"layer":"DIM"})
    d.render()

def dim_v(msp, y1, y2, x, off=18):
    d = msp.add_linear_dim(base=(x-off, y1), p1=(x,y1), p2=(x,y2),
                            angle=90, dimstyle="P30", dxfattribs={"layer":"DIM"})
    d.render()


def t(msp, x, y, s, h=6, layer="RM"):
    msp.add_text(s, height=h, dxfattribs={"layer":layer}
                 ).set_placement((x,y), align=TextEntityAlignment.MIDDLE_CENTER)


def rect(msp, x, y, w, h, layer="INT"):
    msp.add_lwpolyline([(x,y),(x+w,y),(x+w,y+h),(x,y+h)], close=True, dxfattribs={"layer":layer})


def win(msp, x1, y1, x2, y2):
    msp.add_line((x1,y1),(x2,y2), dxfattribs={"layer":"WIN","lineweight":35})
    dx,dy = x2-x1, y2-y1
    ln = max(math.sqrt(dx*dx+dy*dy), 0.01)
    nx,ny = -dy/ln*2, dx/ln*2
    msp.add_line((x1+nx,y1+ny),(x2+nx,y2+ny), dxfattribs={"layer":"WIN"})
    msp.add_line((x1-nx,y1-ny),(x2-nx,y2-ny), dxfattribs={"layer":"WIN"})


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

    # === EXTERIOR WALLS ===
    rect(msp, 0, 0, HOUSE_EW_ACTUAL, HOUSE_NS, "EXT")
    rect(msp, EXT, EXT, HOUSE_EW_ACTUAL-2*EXT, HOUSE_NS-2*EXT, "EXT")

    # === BACK ROOMS EAST WALL (between back rooms and kitchen/eating) ===
    rect(msp, BACK_E, DIN_S, INT, SUN_N - DIN_S, "INT")

    # === SUN/DINING DIVIDER WALL (E-W wall between dining room south and sunroom north) ===
    rect(msp, EXT, SUN_DIN_WALL_S, BACK_E - EXT, INT, "INT")

    # === KITCHEN WALLS ===
    # Kitchen N wall (= sun/din divider extended east)
    rect(msp, BACK_WALL_E, SUN_DIN_WALL_S, kit_x2 - BACK_WALL_E, INT, "INT")
    # Kitchen has NO south wall (open to eating area per user)
    # Kitchen east wall or opening to living room - leave open for now

    # === DEN WALLS ===
    # Den N wall (= dining room S wall = kitchen S edge extended east)
    rect(msp, den_x1, DIN_S - INT, DEN_EW, INT, "INT")
    # Den W wall
    rect(msp, den_x1 - INT, DEN_S, INT, DEN_NS, "INT")

    # === LIVING ROOM WALLS ===
    # LR S wall (partial, from den area east to east wall)
    rect(msp, den_x2, LR_S - INT, EAST_INT - den_x2, INT, "INT")
    # LR W wall (from LR_S to north wall)
    rect(msp, LR_W - INT, LR_S, INT, LR_N - LR_S, "INT")

    # === SUNROOM ===
    t(msp, (sun_x1+sun_x2)/2, (sun_y1+sun_y2)/2+15, "SUNROOM", 7)
    t(msp, (sun_x1+sun_x2)/2, (sun_y1+sun_y2)/2, f"{il(SUNROOM_NS)} x {il(BACK_ROOM_EW)}", 4.5, "DMS")
    t(msp, (sun_x1+sun_x2)/2, (sun_y1+sun_y2)/2-15, "(Slate, Arched Windows)", 3.5, "DMS")

    # === DINING ROOM ===
    t(msp, (din_x1+din_x2)/2, (din_y1+din_y2)/2+15, "DINING ROOM", 7)
    t(msp, (din_x1+din_x2)/2, (din_y1+din_y2)/2, f"{il(DINING_NS)} x {il(BACK_ROOM_EW)}", 4.5, "DMS")
    t(msp, (din_x1+din_x2)/2, (din_y1+din_y2)/2-15, "(Hardwood, Crown Molding)", 3.5, "DMS")

    # === KITCHEN ===
    t(msp, (kit_x1+kit_x2)/2, (kit_y1+kit_y2)/2+10, "KITCHEN", 7)
    t(msp, (kit_x1+kit_x2)/2, (kit_y1+kit_y2)/2-8, "(Tile Floor)", 3.5, "DMS")

    # === EATING AREA ===
    t(msp, (eat_x1+eat_x2)/2, (eat_y1+eat_y2)/2+10, "EATING AREA", 7)
    t(msp, (eat_x1+eat_x2)/2, (eat_y1+eat_y2)/2-8, "(Tile Floor, Coffered Ceiling)", 3.5, "DMS")

    # === LIVING ROOM ===
    t(msp, (lr_x1+lr_x2)/2, (lr_y1+lr_y2)/2+25, "LIVING ROOM", 8)
    t(msp, (lr_x1+lr_x2)/2, (lr_y1+lr_y2)/2+10, f"~{il(LR_FRONT_TO_STAIRS+STAIR_NS)} x {il(235)}", 4.5, "DMS")
    t(msp, (lr_x1+lr_x2)/2, (lr_y1+lr_y2)/2-5, "(Carpet, Crown Molding, Brick FP)", 3.5, "DMS")

    # === DEN ===
    t(msp, (den_x1+den_x2)/2, (den_y1+den_y2)/2+15, "DEN", 7)
    t(msp, (den_x1+den_x2)/2, (den_y1+den_y2)/2, f"{il(DEN_NS)} x {il(DEN_EW)}", 4.5, "DMS")
    t(msp, (den_x1+den_x2)/2, (den_y1+den_y2)/2-15, "(Hardwood)", 3.5, "DMS")

    # === FRONT ENTRANCE ===
    t(msp, (den_x2 + lr_x1)/2, (ENTRANCE_S+ENTRANCE_N)/2, "FRONT", 5)
    t(msp, (den_x2 + lr_x1)/2, (ENTRANCE_S+ENTRANCE_N)/2-10, "ENTRANCE", 5)

    # === CLOSET ===
    rect(msp, cl_x1, cl_y1, CLOSET_EW, CLOSET_NS, "INT")
    t(msp, cl_x1+CLOSET_EW/2, (cl_y1+cl_y2)/2+5, "CLOSET", 3, "RM")
    t(msp, cl_x1+CLOSET_EW/2, (cl_y1+cl_y2)/2-5, f"{il(CLOSET_NS)}x{il(CLOSET_EW)}", 2.5, "DMS")

    # === POWDER ROOM ===
    rect(msp, pr_x1, pr_y1, POWDER_EW, POWDER_NS, "INT")
    t(msp, pr_x1+POWDER_EW/2, (pr_y1+pr_y2)/2+5, "POWDER RM", 3, "RM")
    t(msp, pr_x1+POWDER_EW/2, (pr_y1+pr_y2)/2-5, f"{il(POWDER_NS)}x{il(POWDER_EW)}", 2.5, "DMS")

    # === OLD PANTRY ===
    rect(msp, op_x1, op_y1, PANTRY_EW, PANTRY_NS, "INT")
    t(msp, op_x1+PANTRY_EW/2, (op_y1+op_y2)/2+5, "OLD PANTRY", 3, "RM")
    t(msp, op_x1+PANTRY_EW/2, (op_y1+op_y2)/2-5, f"{il(PANTRY_NS)}x{il(PANTRY_EW)}", 2.5, "DMS")

    # === BASEMENT STAIRS ===
    rect(msp, bs_x1, bs_y1, BSMT_STAIR_NS, bs_y2-bs_y1, "STR")
    t(msp, bs_x1+BSMT_STAIR_NS/2, (bs_y1+bs_y2)/2+5, "BSMT", 3.5, "STR")
    t(msp, bs_x1+BSMT_STAIR_NS/2, (bs_y1+bs_y2)/2-5, "STAIRS DN", 3.5, "STR")

    # === MAIN STAIRCASE (UP) ===
    rect(msp, stair_x, stair_y1, STAIR_NS, stair_y2-stair_y1, "STR")
    t(msp, stair_x+STAIR_NS/2, (stair_y1+stair_y2)/2+5, "STAIRS", 3.5, "STR")
    t(msp, stair_x+STAIR_NS/2, (stair_y1+stair_y2)/2-5, "UP", 3.5, "STR")

    # === FIREPLACE ===
    fp_w, fp_h = 72, 22
    rect(msp, fp_x-fp_w/2, fp_y, fp_w, fp_h, "FP")
    t(msp, fp_x, fp_y+fp_h/2, "BRICK FP", 3.5, "FP")

    # === HERRINGBONE FP in eating/dining area ===
    fp2_x = (din_x1+din_x2)/2
    fp2_y = DIN_S - 30
    rect(msp, fp2_x-30, fp2_y, 60, 20, "FP")
    t(msp, fp2_x, fp2_y+10, "HERRINGBONE FP", 3, "FP")

    # === GARAGE ===
    rect(msp, gar_x1, gar_y1, gar_x2-gar_x1, gar_y2-gar_y1, "GAR")
    t(msp, (gar_x1+gar_x2)/2, (gar_y1+gar_y2)/2+10, "GARAGE", 8, "GAR")
    t(msp, (gar_x1+gar_x2)/2, (gar_y1+gar_y2)/2-10, "(dims TBD)", 4, "GAR")

    # === WINDOWS ===
    # Sunroom - west wall windows (backyard)
    win(msp, EXT, sun_y1+20, EXT, sun_y2-20)
    # Dining room - west wall windows
    win(msp, EXT, din_y1+20, EXT, din_y2-20)
    # Living room - north wall windows
    win(msp, lr_x1+20, LR_N, lr_x2-20, LR_N)
    # Living room - east wall windows (front)
    win(msp, EAST_INT, LR_S+30, EAST_INT, LR_N-30)
    # Den - east wall window (front)
    win(msp, EAST_INT, den_y1+20, EAST_INT, den_y2-20)

    # === FRONT DOOR (east wall) ===
    fd_y = (ENTRANCE_S + ENTRANCE_N) / 2
    msp.add_line((EAST_INT, fd_y-18), (EAST_INT, fd_y+18), dxfattribs={"layer":"DOORS"})

    # === DIMENSIONS ===
    # Overall
    dim_h(msp, 0, HOUSE_EW_ACTUAL, 0, off=36)
    dim_v(msp, 0, HOUSE_NS, 0, off=36)

    # Sunroom
    dim_h(msp, sun_x1, sun_x2, sun_y2, off=12)
    dim_v(msp, sun_y1, sun_y2, sun_x1, off=-12)

    # Dining room
    dim_v(msp, din_y1, din_y2, din_x1, off=-12)

    # Den
    dim_h(msp, den_x1, den_x2, den_y1, off=-12)
    dim_v(msp, den_y1, den_y2, den_x2, off=12)

    # Living room
    dim_v(msp, lr_y1, lr_y2, lr_x2, off=24)

    # === COMPASS AND LABELS ===
    cx = HOUSE_EW_ACTUAL + 40
    cy = HOUSE_NS / 2
    msp.add_line((cx,cy),(cx,cy+30), dxfattribs={"layer":"RM"})
    msp.add_line((cx,cy+30),(cx-5,cy+22), dxfattribs={"layer":"RM"})
    msp.add_line((cx,cy+30),(cx+5,cy+22), dxfattribs={"layer":"RM"})
    t(msp, cx, cy+38, "N", 8)

    t(msp, HOUSE_EW_ACTUAL/2, HOUSE_NS+15, "NORTH (Living Room side)", 5, "DMS")
    t(msp, HOUSE_EW_ACTUAL/2, -15, "SOUTH (Garage side)", 5, "DMS")
    t(msp, HOUSE_EW_ACTUAL+15, HOUSE_NS/2+50, "EAST", 5, "DMS")
    t(msp, HOUSE_EW_ACTUAL+15, HOUSE_NS/2+38, "(Front Door/", 3.5, "DMS")
    t(msp, HOUSE_EW_ACTUAL+15, HOUSE_NS/2+28, "Street)", 3.5, "DMS")
    t(msp, -15, HOUSE_NS/2, "WEST", 5, "DMS")
    t(msp, -15, HOUSE_NS/2-12, "(Backyard)", 3.5, "DMS")

    # Title
    t(msp, HOUSE_EW_ACTUAL/2, -35, "30 PARK - GROUND FLOOR PLAN (v5)", 10)
    t(msp, HOUSE_EW_ACTUAL/2, -50,
      "AS-BUILT | Front faces EAST | Ceiling 8'-0\" | Int Walls 5-1/4\"", 4, "DMS")

    out = "/home/paul/Data/workspace/PaulLaurie30Park/docs/current/30park-ground-floor-plan.dxf"
    doc.saveas(out)
    print(f"DXF: {out}")
    return out


if __name__ == "__main__":
    generate()
