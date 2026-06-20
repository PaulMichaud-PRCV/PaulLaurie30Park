# 30 Park — Project Instructions

## Project Overview

Reconstructing the ground-floor plan of the house at 30 Park from hand-drawn measurements and room photos. The goal is an accurate 2D as-built floor plan (DXF), then renovation options, then 3D renderings.

## Current State

The floor plan layout (room positions, dimensions, adjacencies) is correct. The DXF file is in `docs/current/30park-ground-floor-plan.dxf`. Remaining work is visual cleanup: poché walls, proper stair symbols, distinguishing exterior vs interior walls, and general draftsperson-quality refinement.

**DO NOT regenerate the DXF from `generate_floor_plan.py`** — the user has manually edited the DXF. Use FreeCAD MCP tools or ezdxf load-modify-save to make targeted edits, preserving manual changes. A backup of the user's manual edit is at `docs/current/30park-ground-floor-plan.MANUAL-EDIT-backup.dxf`.

## Compass Orientation (Critical)

- **Front door faces EAST** (street side)
- **Backyard faces WEST**
- **Living Room is on the NORTH side**
- **Garage is on the SOUTH side**
- In the DXF: X increases NORTH, Y increases EAST. Drawing is flipped so EAST (front door) appears at the bottom.

## House Structure — 3 Rectangles

Only the garage is a fully walled/contained rectangle. The other two define the footprint but share open walls internally.

- **NORTH rectangle:** Sunroom (10'10"×18'6") + Dining Room (11'8"×18'6") at the west/back. Kitchen (130" N-S, east of sunroom) + Piano Room (11'8"×11'6") in the center. Living Room (~20'3"×19'7") + Bedroom Stairs (double-wide 180°, 78" N-S) at the east/front. Fireplace on the living room's east wall. Piano room is open (no wall) to the living room on its east side.
- **CENTRAL rectangle:** Eating Area (10'6"×15'3"), Den (12'×12'), Powder Room (61"×61"), Closet (72"×24"), Old Pantry (46"×29"), Entry (72" N-S). A 72" open space extends the kitchen southward. West wall = eating area west wall (outdoor to its west). East wall = den east wall.
- **GARAGE:** Own rectangle on the south side. West wall in line with kitchen west wall. East wall in line with living room east outer wall. Dimensions TBD.

## Available Tools for Editing

### FreeCAD MCP Servers (real-time editing)

Two MCP servers are available when FreeCAD is running (RPC auto-starts):

1. **freecad-neka** (`mcp__freecad-neka__*`): Create/edit/delete objects, execute Python code in FreeCAD, query scene, get view screenshots. Key tools:
   - `create_object`, `edit_object`, `delete_object`, `get_object`, `get_objects`
   - `execute_code` — run arbitrary FreeCAD Python directly
   - `get_view` — screenshot the current 3D view
   - `create_document`, `list_documents`

2. **freecad-contextform** (`mcp__freecad-contextform__*`): 45+ operations for PartDesign, Part primitives, booleans, screenshots, view control. Key tools:
   - `check_freecad_connection` — verify FreeCAD is running and responsive

Changes via MCP appear in FreeCAD's viewport in real-time.

### Python Libraries (for DXF manipulation)

- `ezdxf` — read/write/modify DXF files programmatically (load-modify-save, not regenerate)
- `shapely` — polygon operations (union, buffer/offset for poché wall computation)
- `cairosvg` — SVG to PNG conversion for previews

### Preview Generation

Always output previews to `docs/current/` (not /tmp). Pipeline:
```
ezdxf SVGBackend → 30park-ground-floor-plan.svg → cairosvg → 30park-ground-floor-plan.png
```

## Key Files

| File | Purpose |
|------|---------|
| `docs/current/30park-ground-floor-plan.dxf` | The working floor plan (DXF). Opened in FreeCAD. |
| `docs/current/30park-ground-floor-plan.MANUAL-EDIT-backup.dxf` | Backup of user's manual edits |
| `docs/current/generate_floor_plan.py` | Parametric generator (coordinates are correct; DO NOT run to overwrite DXF) |
| `docs/current/30Park-Current-Layout.svg` | User's OmniGraffle reference diagram (authoritative room topology) |
| `docs/current/room-photos/` | Room photographs used to identify rooms |
| `docs/current/room-photos/Photo Jun 19 2026, 10 30 24 PM.jpg` | Hand-drawn measurement diagram |

## Key Measurements

- Interior walls: 5¼" | Exterior walls: ~6" | Ceiling: 96" (8'-0")
- 31'7" = dining room east wall to living room east wall
- Entry wall: 72" (den north to bedroom stairs south)
- Entryway wall to powder room east wall: 11'5"
- Den east wall: 4' west of living room east wall
- Bedroom stairs: each section 3'3" N-S (78" total), south aligned with kitchen south
- Landing (west of bedroom stairs): 38" E-W × 72" N-S, west side 8'4" east of kitchen east wall
- Powder room north wall in line with den north wall
- Eating area south wall = garage north wall
- Stair labels: "Bedroom Stairs" (by living room), "Loft Stairs" (south of den)
