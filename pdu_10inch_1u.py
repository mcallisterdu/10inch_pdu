"""
10-Inch 1U Rack Low-Voltage DC Power Distribution Unit (PDU) Cage & Faceplate (v2 Dry-Fit Layout)
Designed in build123d for Bambu Lab X1C (PETG, support-free flat bed orientation)

Coordinate System:
  X: Width  (-127.0 mm Left to +127.0 mm Right; 254.0 mm = 10" standard)
  Y: Depth  (0.0 mm Front Faceplate to +140.0 mm Rear Bulkhead)
  Z: Height (0.0 mm Tray Floor Bottom to +44.45 mm 1U Top)

Supported Internal Hardware (v2 Layout from Dry-Fit):
  1. Front-Left AC Inlet (IEC C14 + Fuse + Switch, 10A 250V):
     - Cutout: 47.2 mm x 27.5 mm at X = -70.0 mm
     - Mounting: 2x M3 heat-set holes at 56.0 mm horizontal center-to-center
  2. Middle-Left 12V-to-5V Buck Converter (TOBSUN EA50-5V):
     - Body: 52.9 mm (along X) x 50.25 mm (along Y) x 20.0 mm (H)
     - Oriented with back edge along left wall (X = -103.5 mm) and 4 screw terminals facing RIGHT (+X)
     - Mounting: 2x 3.5 mm ear holes at 56.5 mm Y-pitch, 19.0 mm from left edge (X = -84.5 mm)
  3. Front-Center Shelly EM Mini Gen4 Smart Energy Meter (1-Ch 16A):
     - Dimensions: 33.1 mm (W along X) x 28.1 mm (L along Y) x 16.15 mm (H)
     - Oriented with 4 screw terminals facing FRONT (-Y)
     - Mounting: Recessed 1.0 mm floor relief + 4.0 mm proud press-fit retaining cradle (5.0 mm total wall grip)
       with open front wire cutaway and flat floor for optional VHB tape.
  4. Front/Middle-Right 12V Lighting Power Supply (NOVBO ECV-036P-012-31, 36W Non-Dimmable):
     - Base footprint: 89.3 mm (L along X) x 48.1 mm (W along Y; 47.5 mm nominal, 46.9 mm top) x 27.5 mm (H)
     - Bolt holes: 2x diagonal corner ovular slots (5.0 x 4.0 mm) at Front-Left (-X, -Y) and Rear-Right (+X, +Y),
       centered 5.0 mm from width edges and 5.25 mm from length edges
  5. Rear-Left & Rear-Right 4-Position Red Terminal Bus Bars (5V+ Rail & 12V+ Rail):
     - Overall: 65.0 mm (L) x 13.0 mm (ear W) x 36.5 mm (H)
     - Mounting: 2x M4 slots at 55.0 mm center-to-center pitch (mounted via M3 heat-set inserts + alignment stops)
  6. Center-Rear Staggered 8-Position Green Terminal Ground Bus Bar (Shared 12V/5V Negative Rail):
     - Overall: 97.0 mm (L) x 13.0 mm (ear W) x 36.5 mm (H)
     - Mounting: 2x M4 slots at 83.0 mm center-to-center pitch (mounted via M3 heat-set inserts + alignment stops)
"""

import re
import tempfile
import zipfile
from pathlib import Path
from build123d import *

# ==============================================================================
# 1. PARAMETERS & DIMENSIONS (mm)
# ==============================================================================

# 10" 1U Rack Faceplate Standard
FACEPLATE_W = 254.0          # 10.00 inches
FACEPLATE_H = 44.45          # 1U standard height (1.75 inches)
FACEPLATE_T = 4.0            # Front panel thickness (mm)
FACEPLATE_FILLET = 5.5       # Outer corner fillet radius

# M6 Rack Mounting Slots (4x Horizontal Stadium Slots)
MOUNT_X_PITCH = 236.5        # 10" standard mounting hole center-to-center (X = +-118.25)
MOUNT_Z_PITCH = 31.75        # 1U standard vertical hole spacing (Z = 22.225 +- 15.875)
MOUNT_SLOT_W = 10.0          # Stadium slot overall width
MOUNT_SLOT_H = 6.8           # Stadium slot height for M6 screw clearance

# Cage / Tray Envelope
CAGE_OUTER_W = 216.0         # X in [-108.0, +108.0], clears 222.25 mm rack rails & M6 slots
CAGE_DEPTH = 140.0           # Total depth from Y = 0 (front face) to Y = 140.0 (rear face)
WALL_T = 3.0                 # Side & rear wall thickness (inner width = 210.0 mm)
FLOOR_T = 3.5                # Floor thickness (Z in [0.0, 3.5])
SIDE_WALL_H = 30.0           # Side wall height (Z in [0.0, 30.0])
REAR_WALL_H = 28.0           # Rear bulkhead height (Z in [0.0, 28.0])

# M3 Heat-Set Threaded Insert Parameters
M3_INSERT_ID = 4.2           # Bore diameter for standard M3 heat-set insert
M3_BOSS_OD = 9.5             # Outer diameter of mounting standoff boss
STD_BOSS_H = 2.0             # Standoff height above floor for PSU & Buck (Z_top = 5.5 mm)
BUSBAR_BOSS_H = 1.0          # Low-profile standoff for 36.5 mm tall bus bars (Z_top = 4.5 + 36.5 = 41.0 < 44.45 mm)

# Component 1: 120V AC Power Inlet (Front-Left of Faceplate)
AC_X = -70.0                 # Center X on faceplate
AC_Z = FACEPLATE_H / 2.0     # Center Z (22.225 mm)
AC_CUT_W = 47.2              # 46.7 mm body + 0.5 mm PETG clearance
AC_CUT_H = 27.5              # 27.0 mm body + 0.5 mm PETG clearance
AC_CUT_FILLET = 1.0          # Corner radius on rectangular cutout
AC_MOUNT_PITCH = 56.0        # M3 mounting holes center-to-center (X = -98.0, -42.0)

# Component 2: 12V-to-5V Buck Converter (TOBSUN EA50-5V, Middle-Left along Left Wall)
# Rotated so back edge (opposite terminals) is parallel to left wall at X = -103.5,
# and 4 screw terminals face RIGHT (+X) at X = -50.6.
BUCK_L = 52.9                # Extent along X (left back edge to right terminal block edge)
BUCK_W = 50.25               # Body extent along Y (excluding front/rear mounting ears)
BUCK_H = 20.0                # Height
BUCK_MOUNT_PITCH = 56.5      # Center-to-center Y distance between front & rear mounting ears
BUCK_HOLE_FROM_BACK = 19.0   # Distance from back edge (X = -103.5) to mounting hole axis
BUCK_LEFT_X = -103.5         # 1.5 mm clearance from X = -105.0 inner left wall
BUCK_CENTER_X = BUCK_LEFT_X + BUCK_L / 2.0   # -77.05 mm (right terminal face at -50.6 mm)
BUCK_HOLE_X = BUCK_LEFT_X + BUCK_HOLE_FROM_BACK  # -84.50 mm
BUCK_CENTER_Y = 66.5         # Body spans Y in [41.375, 91.625]; ear holes at Y = 38.25 and 94.75

# Component 3: Shelly EM Mini Gen4 Smart Energy Meter (Front-Center Press-Fit Pocket)
# Oriented with 4 screw terminals facing FRONT (-Y).
SHELLY_W = 33.1              # Width along X (terminal side)
SHELLY_L = 28.1              # Length along Y
SHELLY_H = 16.15             # Height along Z
SHELLY_TOL = 0.25            # Total press-fit clearance (+0.125 mm per side)
SHELLY_POCKET_W = SHELLY_W + SHELLY_TOL  # 33.35 mm
SHELLY_POCKET_L = SHELLY_L + SHELLY_TOL  # 28.35 mm
SHELLY_RELIEF_DEPTH = 1.0    # 1.0 mm recess into the 3.5 mm floor (pocket floor at Z = 2.5 mm)
SHELLY_RIM_H = 4.0           # 4.0 mm proud retaining wall above floor (5.0 mm total wall height from Z = 2.5 to 7.5)
SHELLY_WALL_T = 2.2          # Retaining frame wall thickness
SHELLY_CENTER_X = -21.0      # Spans X in [-37.675, -4.325] (clears Buck terminals at -50.6 & PSU at +5.35)
SHELLY_CENTER_Y = 53.0       # Spans Y in [38.825, 67.175] (terminals at Y = 38.825 facing front)

# Component 4: New 12V Power Supply (NOVBO ECV-036P-012-31, Front/Middle-Right)
# Tapered body: base is 89.3 x 48.1 mm (nominal width 47.5 mm, top 88.3 x 46.9 mm), height 27.5 mm.
# Ovular bolt holes (5.0 mm L x 4.0 mm W) at Front-Left (-X, -Y) and Rear-Right (+X, +Y) corners,
# centered 5.0 mm from width edges and 5.25 mm from length edges.
PSU_BASE_L = 89.3            # Base length along X
PSU_BASE_W = 48.1            # Base width along Y (nominal 47.5 mm)
PSU_NOM_W = 47.5             # Nominal width for hole inset reference
PSU_H = 27.5                 # Height
PSU_HOLE_INSET_Y = 5.0       # 5.0 mm from width edges
PSU_HOLE_INSET_X = 5.25      # 5.25 mm from length edges (centers M3 screw in 5x4 mm oval slot)
PSU_HOLE_DX = PSU_BASE_L / 2.0 - PSU_HOLE_INSET_X  # 44.65 - 5.25 = 39.40 mm (78.80 mm X-pitch)
PSU_HOLE_DY = (PSU_BASE_W + PSU_NOM_W) / 4.0 - PSU_HOLE_INSET_Y  # 23.90 - 5.0 = 18.90 mm (37.80 mm Y-pitch)
PSU_CENTER_X = 50.0          # Base spans X in [+5.35, +94.65] (10.35 mm right wall clearance)
PSU_CENTER_Y = 46.0          # Base spans Y in [21.95, 70.05]

# Component 5: 2x Red 4-Position Terminal Bus Bars (5V+ Left & 12V+ Right, Rear Row)
BUS4_L = 65.0                # Overall length
BUS4_EAR_W = 13.0            # Mounting ear width
BUS4_BODY_W = 16.5           # Body width envelope with red cover
BUS4_H = 36.5                # Total height with cover
BUS4_PITCH = 55.0            # Center-to-center mounting slot spacing
BUS4_LEFT_X = -66.0          # Rear-Left (5V+ rail): spans X in [-98.5, -33.5], holes at -93.5 & -38.5
BUS4_RIGHT_X = 66.0          # Rear-Right (12V+ rail): spans X in [+33.5, +98.5], holes at +38.5 & +93.5
BUS4_Y = 119.0               # Rear row Y center (18 mm in front of rear wall for outgoing wire loops)

# Component 6: 1x Green 8-Position Terminal Ground Bus Bar (Shared Negative Rail, Center-Rear Staggered)
BUS8_L = 97.0                # Overall length
BUS8_EAR_W = 13.0            # Mounting ear width
BUS8_BODY_W = 16.5           # Body width envelope with green cover
BUS8_H = 36.5                # Total height with cover
BUS8_PITCH = 83.0            # Center-to-center mounting slot spacing
BUS8_CENTER_X = 0.0          # Spans X in [-48.5, +48.5], holes at -41.5 & +41.5 (clears Buck at -50.6)
BUS8_Y = 95.0                # Staggered 24.0 mm forward of the two Red Bus Bars (Y = 119.0)


# ==============================================================================
# 2. BUILD MODEL GEOMETRY
# ==============================================================================

def build_pdu() -> Part:
    with BuildPart() as pdu:
        # ----------------------------------------------------------------------
        # A. FRONT FACEPLATE (Y in [0.0, 4.0])
        # ----------------------------------------------------------------------
        with BuildSketch(Plane.XZ) as fp_sk:
            Rectangle(FACEPLATE_W, FACEPLATE_H, align=(Align.CENTER, Align.MIN))
            fillet(fp_sk.vertices(), radius=FACEPLATE_FILLET)

            # 4x M6 Rack Mounting Slots
            for sx in (-MOUNT_X_PITCH / 2.0, MOUNT_X_PITCH / 2.0):
                for sz in (FACEPLATE_H / 2.0 - MOUNT_Z_PITCH / 2.0, FACEPLATE_H / 2.0 + MOUNT_Z_PITCH / 2.0):
                    with Locations((sx, sz)):
                        SlotOverall(MOUNT_SLOT_W, MOUNT_SLOT_H, mode=Mode.SUBTRACT)

            # 2x M3 Heat-Set Insert Mounting Holes for AC Inlet (56.0 mm pitch)
            for dx in (-AC_MOUNT_PITCH / 2.0, AC_MOUNT_PITCH / 2.0):
                with Locations((AC_X + dx, AC_Z)):
                    Circle(M3_INSERT_ID / 2.0, mode=Mode.SUBTRACT)

        extrude(amount=-FACEPLATE_T)  # Plane.XZ normal is -Y, so -FACEPLATE_T extrudes into +Y [0, +4.0]

        # Rear reinforcement bosses on faceplate for AC Inlet M3 heat-set inserts (Y in [4.0, 6.0])
        with BuildSketch(Plane.XZ.offset(-FACEPLATE_T)):
            for dx in (-AC_MOUNT_PITCH / 2.0, AC_MOUNT_PITCH / 2.0):
                with Locations((AC_X + dx, AC_Z)):
                    Circle(M3_BOSS_OD / 2.0)
                    Circle(M3_INSERT_ID / 2.0, mode=Mode.SUBTRACT)
        extrude(amount=-2.0)

        # Cut the 120V AC Inlet Rectangular Body Cutout cleanly through both faceplate and rear boss (Y in [0, 6.5])
        with BuildSketch(Plane.XZ):
            with Locations((AC_X, AC_Z)):
                RectangleRounded(AC_CUT_W, AC_CUT_H, AC_CUT_FILLET)
        extrude(amount=-(FACEPLATE_T + 2.5), mode=Mode.SUBTRACT)

        # ----------------------------------------------------------------------
        # B. CAGE FLOOR & PERIMETER WALLS (X in [-108, +108], Y in [4.0, 140.0])
        # ----------------------------------------------------------------------
        # Floor plate (Z in [0.0, FLOOR_T])
        with BuildSketch(Plane.XY):
            with Locations((0.0, FACEPLATE_T)):
                Rectangle(CAGE_OUTER_W, CAGE_DEPTH - FACEPLATE_T, align=(Align.CENTER, Align.MIN))
        extrude(amount=FLOOR_T)

        # Left & Right Side Walls (X = +-106.5 center, Y in [4.0, 140.0], Z in [0.0, SIDE_WALL_H])
        for side_x in (-CAGE_OUTER_W / 2.0 + WALL_T / 2.0, CAGE_OUTER_W / 2.0 - WALL_T / 2.0):
            with BuildSketch(Plane.XY):
                with Locations((side_x, FACEPLATE_T)):
                    Rectangle(WALL_T, CAGE_DEPTH - FACEPLATE_T, align=(Align.CENTER, Align.MIN))
            extrude(amount=SIDE_WALL_H)

        # Front-to-Side-Wall Full-Height Buttress Pillars at Y in [4.0, 18.0] (Z in [30.0, 44.45])
        for side_x in (-CAGE_OUTER_W / 2.0 + WALL_T / 2.0, CAGE_OUTER_W / 2.0 - WALL_T / 2.0):
            with BuildSketch(Plane.YZ.offset(side_x - WALL_T / 2.0)):
                Polygon(
                    (FACEPLATE_T, SIDE_WALL_H),
                    (FACEPLATE_T, FACEPLATE_H),
                    (FACEPLATE_T + 14.0, SIDE_WALL_H),
                    align=None,
                )
            extrude(amount=WALL_T)

        # Lateral Wing Gussets tying the 254 mm faceplate ears (behind X in [108, 112.5]) to the cage walls
        for sign in (-1.0, 1.0):
            for gz in (0.0, FACEPLATE_H - WALL_T):
                with BuildSketch(Plane.XY.offset(gz)):
                    Polygon(
                        (sign * (CAGE_OUTER_W / 2.0), FACEPLATE_T),
                        (sign * (CAGE_OUTER_W / 2.0 + 4.5), FACEPLATE_T),
                        (sign * (CAGE_OUTER_W / 2.0), FACEPLATE_T + 9.0),
                        align=None,
                    )
                extrude(amount=WALL_T)

        # Rear Bulkhead Wall (Y in [137.0, 140.0], Z in [0.0, REAR_WALL_H])
        with BuildSketch(Plane.XY):
            with Locations((0.0, CAGE_DEPTH - WALL_T)):
                Rectangle(CAGE_OUTER_W, WALL_T, align=(Align.CENTER, Align.MIN))
        extrude(amount=REAR_WALL_H)

        # ----------------------------------------------------------------------
        # C. PROTECTIVE 120V AC ISOLATION BAFFLE (With Right Exit to Shelly & PSU)
        # ----------------------------------------------------------------------
        # Shields the 120V AC inlet quick-disconnect lugs from the TOBSUN Buck Converter behind it (Y >= 36 mm)
        # while providing an open pass-through gap on the right (Y in [16, 33]) toward the Shelly & NOVBO PSU AC input.
        AC_BAFFLE_H = 24.0
        with BuildSketch(Plane.XY.offset(FLOOR_T)):
            # Front-right short return wall at X = -34.0, Y in [4.0, 15.0] (clears AC boss at X = -37.25)
            with Locations((-34.0, FACEPLATE_T)):
                Rectangle(2.5, 11.0, align=(Align.CENTER, Align.MIN))
            # Rear shield wall at Y = 33.0, X in [-96.0, -42.0] (clears Buck front ear boss at X=-84.5, Y=38.25)
            with Locations((-69.0, 33.0)):
                Rectangle(54.0, 2.5, align=(Align.CENTER, Align.CENTER))
        extrude(amount=AC_BAFFLE_H)

        # ----------------------------------------------------------------------
        # D. SHELLY EM MINI GEN4 PRESS-FIT & VHB CRADLE POCKET
        # ----------------------------------------------------------------------
        # 1. Subtract the 1.0 mm deep inner press-fit relief pocket (33.35 x 28.35 mm) into the 3.5 mm floor (Z = 2.5..3.5)
        with BuildSketch(Plane.XY.offset(FLOOR_T)):
            with Locations((SHELLY_CENTER_X, SHELLY_CENTER_Y)):
                RectangleRounded(SHELLY_POCKET_W, SHELLY_POCKET_L, 0.8)
        extrude(amount=-SHELLY_RELIEF_DEPTH, mode=Mode.SUBTRACT)

        # 2. Extrude the 4.0 mm proud press-fit retaining cradle tabs around the pocket perimeter (Z = 3.5..7.5 mm)
        #    Leaves a 23.0 mm wide open front (-Y) cutaway for the 4 screw terminals (O, O, L, N)
        #    and 8.0 mm side gaps on Left/Right for easy finger grip.
        with BuildSketch(Plane.XY.offset(FLOOR_T)):
            with Locations((SHELLY_CENTER_X, SHELLY_CENTER_Y)):
                # Rear wall (+Y)
                with Locations((0.0, SHELLY_POCKET_L / 2.0 + SHELLY_WALL_T / 2.0)):
                    Rectangle(SHELLY_POCKET_W + 2 * SHELLY_WALL_T, SHELLY_WALL_T)
                # Front-Left & Front-Right corner retainer lips (-Y, leaving center 23.35 mm open for terminals)
                for sx in (-1.0, 1.0):
                    with Locations((sx * (SHELLY_POCKET_W / 2.0 - 2.5 + SHELLY_WALL_T / 2.0), -SHELLY_POCKET_L / 2.0 - SHELLY_WALL_T / 2.0)):
                        Rectangle(5.0 + SHELLY_WALL_T, SHELLY_WALL_T)
                # Left & Right side walls (split into front and rear segments with central 8.0 mm finger-pry gap)
                for sx in (-1.0, 1.0):
                    for sy in (-1.0, 1.0):
                        seg_len = (SHELLY_POCKET_L - 8.0) / 2.0
                        with Locations((sx * (SHELLY_POCKET_W / 2.0 + SHELLY_WALL_T / 2.0), sy * (SHELLY_POCKET_L / 2.0 - seg_len / 2.0))):
                            Rectangle(SHELLY_WALL_T, seg_len)
        extrude(amount=SHELLY_RIM_H)

        # ----------------------------------------------------------------------
        # E. COMPONENT MOUNTING BOSSES (M3 Heat-Set Threaded Inserts)
        # ----------------------------------------------------------------------
        # 1. Standard-height (2.0 mm proud, Z_top = 5.5 mm) M3 bosses:
        #    - TOBSUN EA50-5V Buck Converter (2x front/rear ears at X = -84.50, Y = 66.5 +- 28.25)
        #    - NOVBO 12V Power Supply (2x diagonal corner ears: Front-Left & Rear-Right)
        std_boss_coords = [
            # TOBSUN EA50-5V Buck Converter ears (56.5 mm Y-pitch, 19.0 mm from left edge)
            (BUCK_HOLE_X, BUCK_CENTER_Y - BUCK_MOUNT_PITCH / 2.0),
            (BUCK_HOLE_X, BUCK_CENTER_Y + BUCK_MOUNT_PITCH / 2.0),
            # NOVBO 12V Power Supply diagonal bolt holes (Front-Left -X/-Y & Rear-Right +X/+Y)
            (PSU_CENTER_X - PSU_HOLE_DX, PSU_CENTER_Y - PSU_HOLE_DY),
            (PSU_CENTER_X + PSU_HOLE_DX, PSU_CENTER_Y + PSU_HOLE_DY),
        ]

        # Flat leveling support pads (2.0 mm proud, Z_top = 5.5 mm, no hole) under unbolted corners
        std_support_pads = [
            # TOBSUN Buck Converter right-side (terminal side) support pads
            (BUCK_CENTER_X + BUCK_L / 2.0 - 5.5, BUCK_CENTER_Y - BUCK_W / 2.0 + 5.5),
            (BUCK_CENTER_X + BUCK_L / 2.0 - 5.5, BUCK_CENTER_Y + BUCK_W / 2.0 - 5.5),
            # NOVBO 12V Power Supply other 2 corners (Front-Right +X/-Y & Rear-Left -X/+Y)
            (PSU_CENTER_X + PSU_HOLE_DX, PSU_CENTER_Y - PSU_HOLE_DY),
            (PSU_CENTER_X - PSU_HOLE_DX, PSU_CENTER_Y + PSU_HOLE_DY),
        ]

        # 2. Low-profile (1.0 mm proud, Z_top = 4.5 mm) M3 bosses for the 3 Bus Bars (36.5 mm tall -> 41.0 mm top):
        #    - Rear-Left Red 4-Position Bus Bar (5V+ Rail, 55.0 mm pitch)
        #    - Rear-Right Red 4-Position Bus Bar (12V+ Rail, 55.0 mm pitch)
        #    - Center-Rear Staggered Green 8-Position Ground Bus Bar (GND Rail, 83.0 mm pitch)
        busbar_boss_coords = [
            # Rear-Left 4-Way Red Bus Bar (5V+)
            (BUS4_LEFT_X - BUS4_PITCH / 2.0, BUS4_Y),
            (BUS4_LEFT_X + BUS4_PITCH / 2.0, BUS4_Y),
            # Rear-Right 4-Way Red Bus Bar (12V+)
            (BUS4_RIGHT_X - BUS4_PITCH / 2.0, BUS4_Y),
            (BUS4_RIGHT_X + BUS4_PITCH / 2.0, BUS4_Y),
            # Center-Rear 8-Way Green Ground Bus Bar (Shared GND)
            (BUS8_CENTER_X - BUS8_PITCH / 2.0, BUS8_Y),
            (BUS8_CENTER_X + BUS8_PITCH / 2.0, BUS8_Y),
        ]

        # Extrude standard 2.0 mm proud bosses + leveling pads (top at Z = 5.5 mm)
        with BuildSketch(Plane.XY.offset(FLOOR_T)):
            for bx, by in std_boss_coords:
                with Locations((bx, by)):
                    Circle(M3_BOSS_OD / 2.0)
            for px, py in std_support_pads:
                with Locations((px, py)):
                    Circle(4.0)
        extrude(amount=STD_BOSS_H)

        # Extrude bus bar 1.0 mm proud bosses + center body support pads (top at Z = 4.5 mm)
        with BuildSketch(Plane.XY.offset(FLOOR_T)):
            for bx, by in busbar_boss_coords:
                with Locations((bx, by)):
                    Circle(M3_BOSS_OD / 2.0)
            # Center anti-flex support pads under each bus bar bridge
            for cx, cy in ((BUS4_LEFT_X, BUS4_Y), (BUS4_RIGHT_X, BUS4_Y), (BUS8_CENTER_X, BUS8_Y)):
                with Locations((cx, cy)):
                    Rectangle(14.0, BUS4_EAR_W)
        extrude(amount=BUSBAR_BOSS_H)

        # Cut M3 heat-set insert blind bores into standard bosses (from Z = 5.5 down to Z = 1.2)
        with BuildSketch(Plane.XY.offset(FLOOR_T + STD_BOSS_H)):
            for bx, by in std_boss_coords:
                with Locations((bx, by)):
                    Circle(M3_INSERT_ID / 2.0)
        extrude(amount=-4.3, mode=Mode.SUBTRACT)

        # Cut M3 heat-set insert blind bores into bus bar bosses (from Z = 4.5 down to Z = 1.0)
        with BuildSketch(Plane.XY.offset(FLOOR_T + BUSBAR_BOSS_H)):
            for bx, by in busbar_boss_coords:
                with Locations((bx, by)):
                    Circle(M3_INSERT_ID / 2.0)
        extrude(amount=-3.5, mode=Mode.SUBTRACT)

        # ----------------------------------------------------------------------
        # F. SQUARE ALIGNMENT GUIDE RIBS FOR PSU, BUCK CONVERTER & BUS BARS
        # ----------------------------------------------------------------------
        # Ensures every component seats 100% square to the chassis axes before tightening screws.
        with BuildSketch(Plane.XY.offset(FLOOR_T)):
            # 1. NOVBO 12V Power Supply front & rear alignment guide tabs (89.3 x 48.1 mm base + 0.35 mm clearance/side)
            for gx in (PSU_CENTER_X - 22.0, PSU_CENTER_X + 22.0):
                with Locations((gx, PSU_CENTER_Y - PSU_BASE_W / 2.0 - 1.35)):
                    Rectangle(16.0, 2.0)
                with Locations((gx, PSU_CENTER_Y + PSU_BASE_W / 2.0 + 1.35)):
                    Rectangle(16.0, 2.0)
            # 2. TOBSUN Buck Converter left-edge backstop ribs (registers back face at X = -103.5 mm, bonded into left wall)
            for gy in (BUCK_CENTER_Y - 14.0, BUCK_CENTER_Y + 14.0):
                with Locations((BUCK_LEFT_X - 1.25, gy)):
                    Rectangle(2.5, 10.0)
        extrude(amount=STD_BOSS_H + 1.8)

        # 3. Bus Bar Square Alignment Channels (front & rear ear guide ledges around the 13.0 mm ears)
        with BuildSketch(Plane.XY.offset(FLOOR_T)):
            for bx in (BUS4_LEFT_X - BUS4_PITCH / 2.0, BUS4_LEFT_X + BUS4_PITCH / 2.0,
                       BUS4_RIGHT_X - BUS4_PITCH / 2.0, BUS4_RIGHT_X + BUS4_PITCH / 2.0):
                with Locations((bx, BUS4_Y + BUS4_EAR_W / 2.0 + 1.2)):
                    Rectangle(10.0, 1.8)
                with Locations((bx, BUS4_Y - BUS4_EAR_W / 2.0 - 1.2)):
                    Rectangle(10.0, 1.8)
            for bx in (BUS8_CENTER_X - BUS8_PITCH / 2.0, BUS8_CENTER_X + BUS8_PITCH / 2.0):
                with Locations((bx, BUS8_Y + BUS8_EAR_W / 2.0 + 1.2)):
                    Rectangle(10.0, 1.8)
                with Locations((bx, BUS8_Y - BUS8_EAR_W / 2.0 - 1.2)):
                    Rectangle(10.0, 1.8)
        extrude(amount=BUSBAR_BOSS_H + 1.8)

        # ----------------------------------------------------------------------
        # G. BOTTOM FLOOR VENTILATION SLOTS & FLUSH ZIP-TIE ANCHOR BRIDGES
        # ----------------------------------------------------------------------
        # 1. Ventilation slots under the NOVBO 12V PSU and TOBSUN Buck Converter
        with BuildSketch(Plane.XY):
            # Under NOVBO 12V Power Supply (X in [+22, +78], Y = 46.0)
            for vx in range(22, 80, 14):
                with Locations((vx, PSU_CENTER_Y)):
                    SlotOverall(26.0, 6.0, rotation=90)
            # Under TOBSUN Buck Converter (X = -68.0, Y in [50, 83])
            for vy in (52.0, 66.5, 81.0):
                with Locations((BUCK_CENTER_X + 6.0, vy)):
                    SlotOverall(20.0, 5.5, rotation=0)
        extrude(amount=FLOOR_T, mode=Mode.SUBTRACT)

        # 2. Flush Zip-Tie Anchor Bridges for Clean Wire Management
        ziptie_anchors = [
            # Front wire corridor (between AC Inlet / Shelly / PSU front)
            (-36.0, 22.0, 0),
            (-10.0, 22.0, 0),
            # Between TOBSUN Buck terminals, Shelly, and Green 8-Way Bus Bar
            (-45.0, 78.0, 90),
            (-21.0, 78.0, 0),
            (15.0, 78.0, 0),
            (85.0, 82.0, 90),
            # Right side 12V output channel (next to NOVBO PSU output)
            (98.0, 46.0, 90),
            # Rear wire exit channels (between Bus Bars and Rear Wall ports)
            (-66.0, 132.0, 0),
            (-16.0, 118.0, 0),
            (16.0, 118.0, 0),
            (66.0, 132.0, 0),
        ]

        # Cut the pair of vertical zip-tie entry/exit slots all the way through the floor
        with BuildSketch(Plane.XY):
            for zx, zy, rot in ziptie_anchors:
                with Locations((zx, zy)):
                    if rot == 0:
                        with Locations((-4.0, 0.0), (4.0, 0.0)):
                            Rectangle(2.4, 5.0)
                    else:
                        with Locations((0.0, -4.0), (0.0, 4.0)):
                            Rectangle(5.0, 2.4)
        extrude(amount=FLOOR_T, mode=Mode.SUBTRACT)

        # Cut the underside recessed channel (Z in [0.0, 1.5]) bridging between each slot pair
        with BuildSketch(Plane.XY):
            for zx, zy, rot in ziptie_anchors:
                with Locations((zx, zy)):
                    if rot == 0:
                        Rectangle(10.4, 5.0)
                    else:
                        Rectangle(5.0, 10.4)
        extrude(amount=1.5, mode=Mode.SUBTRACT)

        # ----------------------------------------------------------------------
        # H. SIDE-WALL AIRFLOW WINDOWS (Support-Free Stadium Slots, Left & Right Walls Only)
        # ----------------------------------------------------------------------
        for wall_x in (-CAGE_OUTER_W / 2.0 + WALL_T / 2.0, CAGE_OUTER_W / 2.0 - WALL_T / 2.0):
            with BuildSketch(Plane.YZ.offset(wall_x)):
                for wy in (32.0, 56.0, 80.0, 104.0, 124.0):
                    with Locations((wy, 16.5)):
                        SlotOverall(16.0, 12.0, rotation=90)
            extrude(amount=WALL_T, both=True, mode=Mode.SUBTRACT)

        # ----------------------------------------------------------------------
        # I. REAR BULKHEAD PASS-THROUGHS & STRAIN-RELIEF LOOPS (Y in [137, 140])
        # ----------------------------------------------------------------------
        rear_port_xs = [-80.0, -48.0, -16.0, 16.0, 48.0, 80.0]

        with BuildSketch(Plane.XZ.offset(-CAGE_DEPTH)):
            for px in rear_port_xs:
                # Top U-channel cable exit slot (8.0 mm wide, from Z = 15.0 to Z = 28.0)
                with Locations((px, 21.5)):
                    SlotOverall(15.0, 8.0, rotation=90)
                # Paired zip-tie strain-relief slots on either side of the cable exit (Z = 10.0)
                with Locations((px - 6.5, 10.0), (px + 6.5, 10.0)):
                    Rectangle(2.4, 5.0)
        extrude(amount=WALL_T + 1.0, mode=Mode.SUBTRACT)

    return pdu.part


def export_bambu_3mf(shape: Part, out_path: str) -> None:
    """Export a BambuStudio-compatible 3MF project with X1C PETG config & centered build plate placement."""
    with tempfile.NamedTemporaryFile(suffix=".3mf", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    mesher = Mesher()
    mesher.add_shape(shape)
    mesher.write(str(tmp_path))

    with zipfile.ZipFile(tmp_path, "r") as zin:
        raw_model = zin.read("3D/3dmodel.model").decode("utf-8")
    tmp_path.unlink(missing_ok=True)

    mesh_match = re.search(r"<mesh>.*?</mesh>", raw_model, flags=re.DOTALL)
    if not mesh_match:
        raise RuntimeError("Could not find <mesh> in generated 3MF")

    bb = shape.bounding_box()
    cx = (bb.min.X + bb.max.X) / 2.0
    cy = (bb.min.Y + bb.max.Y) / 2.0
    cz = (bb.min.Z + bb.max.Z) / 2.0
    half_z = bb.size.Z / 2.0

    def _shift_vertex(m: re.Match) -> str:
        vx = float(m.group(1)) - cx
        vy = float(m.group(2)) - cy
        vz = float(m.group(3)) - cz
        return f'<vertex x="{vx:.6f}" y="{vy:.6f}" z="{vz:.6f}"/>'

    centered_mesh = re.sub(
        r'<vertex\s+x="([^"]+)"\s+y="([^"]+)"\s+z="([^"]+)"\s*/>',
        _shift_vertex,
        mesh_match.group(0),
    )
    face_count = len(re.findall(r"<triangle\s+", centered_mesh))

    plate_x, plate_y, plate_z = 128.0, 140.0, half_z

    object_1_model = f"""<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">
 <metadata name="BambuStudio:3mfVersion">1</metadata>
 <resources>
  <object id="1" p:UUID="00010000-81cb-4c03-9d28-80fed5dfa1dc" type="model">
   {centered_mesh}
  </object>
 </resources>
 <build/>
</model>
"""

    root_model = f"""<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">
 <metadata name="Application">BambuStudio-02.08.02.61</metadata>
 <metadata name="BambuStudio:3mfVersion">1</metadata>
 <metadata name="CreationDate">2026-11-22</metadata>
 <metadata name="ModificationDate">2026-11-22</metadata>
 <metadata name="Title">10-Inch 1U Rack DC PDU v2</metadata>
 <resources>
  <object id="2" p:UUID="00000001-61cb-4c03-9d28-80fed5dfa1dc" type="model">
   <components>
    <component p:path="/3D/Objects/object_1.model" objectid="1" p:UUID="00010000-b206-40ff-9872-83e8017abed1" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>
   </components>
  </object>
 </resources>
 <build p:UUID="2c7c17d8-22b5-4d84-8835-1976022ea369">
  <item objectid="2" p:UUID="00000002-b1ec-4553-aec9-835e5b724bb4" transform="1 0 0 0 1 0 0 0 1 {plate_x:.4f} {plate_y:.4f} {plate_z:.4f}" printable="1"/>
 </build>
</model>
"""

    model_settings = f"""<?xml version="1.0" encoding="UTF-8"?>
<config>
  <object id="2">
    <metadata key="name" value="pdu_10inch_1u"/>
    <metadata key="extruder" value="1"/>
    <metadata face_count="{face_count}"/>
    <part id="1" subtype="normal_part" uuid="de9f429a-2a02-44ab-b7a8-a7c954651ab5">
      <metadata key="name" value="pdu_10inch_1u"/>
      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>
      <metadata key="source_file" value="pdu_10inch_1u.3mf"/>
      <metadata key="source_object_id" value="0"/>
      <metadata key="source_volume_id" value="0"/>
      <metadata key="source_offset_x" value="{cx:.4f}"/>
      <metadata key="source_offset_y" value="{cy:.4f}"/>
      <metadata key="source_offset_z" value="{cz:.4f}"/>
      <mesh_stat face_count="{face_count}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>
    </part>
  </object>
  <plate>
    <metadata key="plater_id" value="1"/>
    <metadata key="plater_name" value=""/>
    <metadata key="locked" value="false"/>
    <metadata key="filament_map_mode" value="Auto For Flush"/>
    <metadata key="filament_maps" value="1"/>
    <metadata key="filament_volume_maps" value="1 0"/>
    <model_instance>
      <metadata key="object_id" value="2"/>
      <metadata key="instance_id" value="0"/>
      <metadata key="identify_id" value="210"/>
    </model_instance>
  </plate>
  <assemble>
   <assemble_item object_id="2" instance_id="0" transform="1 0 0 0 1 0 0 0 1 {plate_x:.4f} {plate_y:.4f} {plate_z:.4f}" offset="0 0 0" />
   <assemble_item object_id="2" volume_id="0" transform="1 0 0 0 1 0 0 0 1 0 0 0" />
  </assemble>
</config>
"""

    slice_info = """<?xml version="1.0" encoding="UTF-8"?>
<config>
  <header>
    <header_item key="X-BBL-Client-Type" value="slicer"/>
    <header_item key="X-BBL-Client-Version" value="02.08.02.61"/>
  </header>
</config>
"""

    cut_info = """<?xml version="1.0" encoding="UTF-8"?>
<objects>
 <object id="1">
  <cut_id id="0" check_sum="1" connectors_cnt="0"/>
 </object>
</objects>
"""

    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
 <Default Extension="png" ContentType="image/png"/>
 <Default Extension="gcode" ContentType="text/x.gcode"/>
</Types>
"""

    root_rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>
"""

    model_rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Target="/3D/Objects/object_1.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>
"""

    proj_cfg_path = Path(__file__).resolve().parent / "bambu_x1c_petg_project_settings.json"
    proj_cfg_bytes = proj_cfg_path.read_bytes()

    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        zout.writestr("[Content_Types].xml", content_types)
        zout.writestr("_rels/.rels", root_rels)
        zout.writestr("3D/3dmodel.model", root_model)
        zout.writestr("3D/_rels/3dmodel.model.rels", model_rels)
        zout.writestr("3D/Objects/object_1.model", object_1_model)
        zout.writestr("Metadata/project_settings.config", proj_cfg_bytes)
        zout.writestr("Metadata/model_settings.config", model_settings)
        zout.writestr("Metadata/slice_info.config", slice_info)
        zout.writestr("Metadata/cut_information.xml", cut_info)
        zout.writestr("Metadata/filament_sequence.json", '{"plate_1":{"nozzle_sequence":[],"optimal_assignment":[],"sequence":[]}}')


if __name__ == "__main__":
    part = build_pdu()
    bb = part.bounding_box()
    print(f"PDU v2 Model Built Successfully!")
    print(f"Bounding Box Min: ({bb.min.X:.2f}, {bb.min.Y:.2f}, {bb.min.Z:.2f}) mm")
    print(f"Bounding Box Max: ({bb.max.X:.2f}, {bb.max.Y:.2f}, {bb.max.Z:.2f}) mm")
    print(f"Overall Size:     {bb.size.X:.2f} W x {bb.size.Y:.2f} D x {bb.size.Z:.2f} H mm")
    print(f"Part Volume:      {part.volume / 1000.0:.2f} cm^3")

    export_step(part, "pdu_10inch_1u.step")
    export_stl(part, "pdu_10inch_1u.stl")
    export_bambu_3mf(part, "pdu_10inch_1u.3mf")

    # Push to standalone OCP CAD Viewer (http://127.0.0.1:3939/viewer) if running
    try:
        from ocp_vscode import Camera, set_port, show
        set_port(3939)
        show(part, names=["pdu_10inch_1u"], port=3939, reset_camera=Camera.RESET)
        print("Pushed model to OCP CAD Viewer at http://127.0.0.1:3939/viewer")
    except Exception as exc:
        print(f"OCP CAD Viewer not active ({exc}); start it with: .venv/bin/python -m ocp_viewer")

    print("Exported pdu_10inch_1u.step, pdu_10inch_1u.stl, and BambuStudio-ready pdu_10inch_1u.3mf")
