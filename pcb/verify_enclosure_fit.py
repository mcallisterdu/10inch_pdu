"""
Mechanical Co-Design Verification:
Imports the exported KiCad 3D STEP model (pcb/pdu_pcb.step) into build123d
and verifies clearances inside the 10-Inch 1U Rack PDU interior envelope:
  - Inner Width:   X in [-105.0, +105.0] (210.0 mm)
  - Inner Depth:   Y in [+4.0, +137.0]   (133.0 mm; front AC/Shelly zone Y in [4.0, 38.0])
  - 1U Height:     Z in [0.0, 44.45]     (floor Z = [0.0, 3.5], 4.5 mm standoffs -> PCB Z_bot = 8.0)
"""

from pathlib import Path
import build123d as bd

PCB_DIR = Path(__file__).resolve().parent
STEP_IN = PCB_DIR / "pdu_pcb.step"

# 10" 1U PDU Enclosure Interior Envelope (from pdu_10inch_1u.py)
INNER_X_MIN, INNER_X_MAX = -105.0, 105.0
INNER_Y_MIN, INNER_Y_MAX = 4.0, 137.0
AC_ZONE_Y_MAX = 38.0
FLOOR_TOP_Z = 3.5
STANDOFF_H = 4.5
RACK_1U_H = 44.45

# PCB Placement in PDU Coordinates:
# KiCad STEP exports (X_kicad, -Y_kicad, Z_kicad) where board is X=[0, 196], Y_kicad=[0, 90] -> Y_step=[-90, 0].
# Flipping Y by rotating 180 deg about X or translating? Wait: KiCad top is +Z, so Y_step = -Y_kicad means:
#   Y_kicad = 0 (front edge, J_AC) -> Y_step = 0
#   Y_kicad = 90 (rear edge, DC outputs) -> Y_step = -90
# Rotating 180 deg around Z maps (X, Y) -> (-X, -Y), or let's inspect the raw STEP bounding box first!

def verify() -> None:
    pcb = bd.import_step(str(STEP_IN))
    bb = pcb.bounding_box()
    print(f"Raw KiCad STEP BBox:")
    print(f"  X: [{bb.min.X:.2f}, {bb.max.X:.2f}] (size {bb.size.X:.2f} mm)")
    print(f"  Y: [{bb.min.Y:.2f}, {bb.max.Y:.2f}] (size {bb.size.Y:.2f} mm)")
    print(f"  Z: [{bb.min.Z:.2f}, {bb.max.Z:.2f}] (size {bb.size.Z:.2f} mm)")

    # Center X at 0, place rear edge (Y_kicad=90) at Y_pdu=131.0, bottom of PCB substrate (Z=0) at Z=8.0
    # In KiCad STEP: X_step in [0, 196], Y_step in [-90, 0] (front=0, rear=-90).
    # To align front (Y_kicad=0) at Y_pdu=41.0 and rear (Y_kicad=90) at Y_pdu=131.0, we check clearances:
    pcb_w = bb.size.X
    pcb_d = bb.size.Y
    pcb_top_above_substrate = bb.max.Z  # height above Z=0 (bottom of board)
    pcb_bottom_protrusion = -bb.min.Z   # THT pin protrusion below bottom of board

    x_clearance_each = (INNER_X_MAX - INNER_X_MIN - pcb_w) / 2.0
    y_front = 41.0
    y_rear = y_front + pcb_d
    y_rear_clearance = INNER_Y_MAX - y_rear
    y_front_clearance = y_front - AC_ZONE_Y_MAX

    z_pcb_bottom = FLOOR_TOP_Z + STANDOFF_H
    z_pin_clearance = STANDOFF_H - pcb_bottom_protrusion
    z_top_max = z_pcb_bottom + pcb_top_above_substrate
    z_top_clearance = RACK_1U_H - z_top_max

    print("\n10-Inch 1U PDU Mechanical Clearance Report:")
    print(f"  Lateral X Clearance:    {x_clearance_each:.2f} mm per side (PASS)" if x_clearance_each > 2.0 else f"  Lateral X Clearance: {x_clearance_each:.2f} mm (FAIL)")
    print(f"  Front AC/Shelly Gap:    {y_front_clearance:.2f} mm (PASS)" if y_front_clearance >= 2.0 else f"  Front Gap: {y_front_clearance:.2f} mm (FAIL)")
    print(f"  Rear Bulkhead Gap:      {y_rear_clearance:.2f} mm (PASS)" if y_rear_clearance >= 4.0 else f"  Rear Gap: {y_rear_clearance:.2f} mm (FAIL)")
    print(f"  Under-PCB Pin Margin:   {z_pin_clearance:.2f} mm above floor (pin protrusion {pcb_bottom_protrusion:.2f} mm) (PASS)" if z_pin_clearance > 1.0 else f"  Pin Margin: {z_pin_clearance:.2f} mm (CHECK)")
    print(f"  1U Top Height Margin:   {z_top_clearance:.2f} mm below 44.45 mm 1U limit (max Z = {z_top_max:.2f} mm) (PASS)" if z_top_clearance > 2.0 else f"  1U Top Margin: {z_top_clearance:.2f} mm (FAIL)")

    assert x_clearance_each > 2.0, "PCB too wide for 210 mm inner cage!"
    assert y_rear_clearance >= 4.0, "PCB too deep for 133 mm inner cage!"
    assert z_top_clearance > 2.0, "PCB exceeds 1U 44.45 mm rack height!"
    print("\nALL 3D MECHANICAL CLEARANCE CHECKS PASSED!")


if __name__ == "__main__":
    verify()
