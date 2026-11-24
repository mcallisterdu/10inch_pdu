"""
10-Inch 1U Rack Low-Voltage DC PDU — Prototype Integrated Power PCB
====================================================================
Replaces off-the-shelf components:
  1. 12V Power Supply       -> Mean Well IRM-60-12 (60W / 5A, or IRM-45-12 45W / 3.75A)
                               UL/TUV/IEC 62368-1 certified Class II encapsulated module
  2. 12V -> 5V Buck         -> TI LMR33640ADDA (36V, 4A, 400kHz synchronous buck, >94% eff.)
  3. 12V / 5V / GND Rails   -> 2 oz copper heavy buses + solid GND plane + 6x Phoenix PT 1,5
                               5.0 mm screw terminals aligned with the 6 PDU rear bulkhead ports
  4. Inline Fuse Holders    -> Integrated PCB-mount fuse sockets:
                               - F_AC: Bulgin FX0457 5x20mm closed holder (2A Slow-Blow 250V)
                               - F1..F8: Keystone 3568 Mini-Blade (ATM/APM) PCB fuse sockets

Board Envelope: 196.0 mm (W) x 90.0 mm (D) x 1.6 mm (T), 2-Layer, 2 oz (70 um) Copper FR-4
Fits inside 10" 1U PDU tray (inner 210 x 133 mm) behind IEC C14 inlet & Shelly EM Mini Gen4.
"""

import os
from pathlib import Path
from skidl import Part as SkidlPart, Net, generate_pcb, reset
import pcbnew

OUT_DIR = Path(__file__).resolve().parent
PCB_FILE = str(OUT_DIR / "pdu_pcb.kicad_pcb")
FP_LIBS = ["/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"]

# Board dimensions (mm)
BOARD_W = 196.0
BOARD_H = 90.0


def mm(val: float) -> int:
    return int(pcbnew.FromMM(val))


def pt(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(mm(x), mm(y))


def generate_netlist_pcb() -> None:
    """Create the complete schematic netlist in SKiDL and generate the initial .kicad_pcb."""
    reset()

    # ==========================================================================
    # NETS
    # ==========================================================================
    ac_l = Net("AC_L")
    ac_l_fused = Net("AC_L_FUSED")
    ac_n = Net("AC_N")

    v12_raw = Net("+12V_RAW")
    v12_bus = Net("+12V_BUS")
    v12_buck_in = Net("+12V_BUCK_IN")

    v5_bus = Net("+5V_BUS")
    gnd = Net("GND")

    # Buck internal nets
    buck_en = Net("BUCK_EN")
    buck_pg = Net("BUCK_PG")
    buck_fb = Net("BUCK_FB")
    buck_vcc = Net("BUCK_VCC")
    buck_boot = Net("BUCK_BOOT")
    buck_sw = Net("BUCK_SW")

    # Fused output channel nets (aligned with 6 rear bulkhead ports)
    v5_ch1 = Net("+5V_CH1_HUE")
    v5_ch2 = Net("+5V_CH2_LUTRON")
    v5_ch3 = Net("+5V_CH3_AUX")
    v12_ch3 = Net("+12V_CH3_AUX")
    v12_ch2 = Net("+12V_CH2_NETGEAR")
    v12_ch1 = Net("+12V_CH1_ODROID")

    # Indicator LED nets
    led12_k = Net("LED12_K")
    led5_k = Net("LED5_K")

    # ==========================================================================
    # 1. AC MAINS PRIMARY INPUT SECTION (120V AC, Isolated Zone)
    # ==========================================================================
    # 3-pin 5.0mm Phoenix terminal block with center pin NC -> 10.0 mm L-N pitch!
    j_ac = SkidlPart(
        "Connector_Generic", "Conn_01x03", ref="J_AC", value="AC_120V_IN",
        footprint="TerminalBlock_Phoenix:TerminalBlock_Phoenix_PT-1,5-3-5.0-H_1x03_P5.00mm_Horizontal",
    )
    j_ac[1] += ac_l
    # Pin 2 intentionally unconnected (spacer for 10.0 mm L-N mains clearance)
    j_ac[3] += ac_n

    # On-board 5x20mm closed AC fuse socket (2A Slow-Blow 250V)
    f_ac = SkidlPart(
        "Device", "Fuse", ref="F_AC", value="2A_T_250V",
        footprint="Fuse:Fuseholder_Cylinder-5x20mm_Bulgin_FX0457_Horizontal_Closed",
    )
    f_ac[1] += ac_l
    f_ac[2] += ac_l_fused

    # AC Mains Surge Protection MOV (150VAC RMS / 240V clamping, 12mm disc, 7.5mm pitch)
    rv1 = SkidlPart(
        "Device", "Varistor", ref="RV1", value="S14K150_MOV",
        footprint="Varistor:RV_Disc_D12mm_W4.2mm_P7.5mm",
    )
    rv1[1] += ac_l_fused
    rv1[2] += ac_n

    # Mean Well IRM-60-12 (60W 12V 5.0A, pin-compatible with IRM-45-12 45W 3.75A)
    u1 = SkidlPart(
        "Converter_ACDC", "IRM-60-12", ref="U1", value="IRM-60-12",
        footprint="Converter_ACDC:Converter_ACDC_MeanWell_IRM-60-xx_THT",
    )
    u1[1] += ac_l_fused   # AC/L
    u1[2] += ac_n         # AC/N
    u1[3] += v12_raw      # +Vout (+12V)
    u1[4] += gnd          # -Vout (GND)

    # ==========================================================================
    # 2. 12V PRIMARY RAIL, MAIN FUSE, BULK FILTERING & TVS
    # ==========================================================================
    f1 = SkidlPart(
        "Device", "Fuse", ref="F1", value="4A_MINI",
        footprint="Fuse:Fuseholder_Blade_Mini_Keystone_3568",
    )
    f1[1] += v12_raw
    f1[2] += v12_bus

    c1 = SkidlPart(
        "Device", "C_Polarized", ref="C1", value="470uF_25V",
        footprint="Capacitor_THT:CP_Radial_D10.0mm_P5.00mm",
    )
    c1[1] += v12_bus
    c1[2] += gnd

    c2 = SkidlPart(
        "Device", "C", ref="C2", value="100nF_25V",
        footprint="Capacitor_SMD:C_0805_2012Metric",
    )
    c2[1] += v12_bus
    c2[2] += gnd

    d1 = SkidlPart(
        "Device", "D_TVS", ref="D1", value="SMBJ15A",
        footprint="Diode_SMD:D_SMB",
    )
    d1[1] += v12_bus   # Cathode
    d1[2] += gnd       # Anode

    led1 = SkidlPart(
        "Device", "LED", ref="LED1", value="12V_OK_GRN",
        footprint="LED_SMD:LED_0805_2012Metric",
    )
    r_led1 = SkidlPart(
        "Device", "R", ref="R_LED1", value="2.2k",
        footprint="Resistor_SMD:R_0805_2012Metric",
    )
    led1[2] += v12_bus    # Anode
    led1[1] += led12_k    # Cathode
    r_led1[1] += led12_k
    r_led1[2] += gnd

    # ==========================================================================
    # 3. 12V -> 5V SYNCHRONOUS BUCK CONVERTER (TI LMR33640ADDA, 4A, 400kHz)
    # ==========================================================================
    f2 = SkidlPart(
        "Device", "Fuse", ref="F2", value="2A_MINI",
        footprint="Fuse:Fuseholder_Blade_Mini_Keystone_3568",
    )
    f2[1] += v12_bus
    f2[2] += v12_buck_in

    u2 = SkidlPart(
        "Regulator_Switching", "LMR33640ADDA", ref="U2", value="LMR33640ADDA",
        footprint="Package_SO:Texas_HSOP-8-1EP_3.9x4.9mm_P1.27mm_ThermalVias",
    )
    u2[1] += gnd          # GND
    u2[2] += v12_buck_in  # VIN
    u2[3] += buck_en      # EN
    u2[4] += buck_pg      # PG
    u2[5] += buck_fb      # FB
    u2[6] += buck_vcc     # VCC
    u2[7] += buck_boot    # BOOT
    u2[8] += buck_sw      # SW
    u2[9] += gnd          # Exposed Thermal Pad (GND)

    # Buck Input Capacitors (low-ESR MLCCs right at VIN)
    c_in1 = SkidlPart("Device", "C", ref="C_IN1", value="22uF_25V", footprint="Capacitor_SMD:C_1206_3216Metric")
    c_in2 = SkidlPart("Device", "C", ref="C_IN2", value="10uF_25V", footprint="Capacitor_SMD:C_1206_3216Metric")
    c_in3 = SkidlPart("Device", "C", ref="C_IN3", value="100nF_25V", footprint="Capacitor_SMD:C_0805_2012Metric")
    for c in (c_in1, c_in2, c_in3):
        c[1] += v12_buck_in
        c[2] += gnd

    # Precision UVLO divider on EN (~9.3V turn-on)
    r_en1 = SkidlPart("Device", "R", ref="R_EN1", value="100k", footprint="Resistor_SMD:R_0805_2012Metric")
    r_en2 = SkidlPart("Device", "R", ref="R_EN2", value="15k", footprint="Resistor_SMD:R_0805_2012Metric")
    r_en1[1] += v12_buck_in
    r_en1[2] += buck_en
    r_en2[1] += buck_en
    r_en2[2] += gnd

    # Internal LDO bypass (VCC) & Bootstrap (BOOT-SW)
    c_vcc = SkidlPart("Device", "C", ref="C_VCC", value="1uF_16V", footprint="Capacitor_SMD:C_0805_2012Metric")
    c_vcc[1] += buck_vcc
    c_vcc[2] += gnd

    c_boot = SkidlPart("Device", "C", ref="C_BOOT", value="100nF_25V", footprint="Capacitor_SMD:C_0805_2012Metric")
    c_boot[1] += buck_boot
    c_boot[2] += buck_sw

    # Shielded Power Inductor (10 uH, 8.5A RMS / 14A Isat, 18 mOhm DCR)
    l1 = SkidlPart("Device", "L", ref="L1", value="10uH_8.5A", footprint="Inductor_SMD:L_Bourns_SRP1245A")
    l1[1] += buck_sw
    l1[2] += v5_bus

    # Feedback Resistor Divider (Vout = 1.0V * (1 + 100k/24.9k) = 5.016V) + C_FF
    r_fb1 = SkidlPart("Device", "R", ref="R_FB1", value="100k_1%", footprint="Resistor_SMD:R_0805_2012Metric")
    r_fb2 = SkidlPart("Device", "R", ref="R_FB2", value="24.9k_1%", footprint="Resistor_SMD:R_0805_2012Metric")
    c_ff = SkidlPart("Device", "C", ref="C_FF", value="22pF", footprint="Capacitor_SMD:C_0805_2012Metric")
    r_pg = SkidlPart("Device", "R", ref="R_PG", value="100k", footprint="Resistor_SMD:R_0805_2012Metric")

    r_fb1[1] += v5_bus
    r_fb1[2] += buck_fb
    r_fb2[1] += buck_fb
    r_fb2[2] += gnd
    c_ff[1] += v5_bus
    c_ff[2] += buck_fb
    r_pg[1] += v5_bus
    r_pg[2] += buck_pg

    # 5V Output Filtering, TVS & Power-OK LED
    c_out1 = SkidlPart("Device", "C", ref="C_OUT1", value="47uF_10V", footprint="Capacitor_SMD:C_1206_3216Metric")
    c_out2 = SkidlPart("Device", "C", ref="C_OUT2", value="47uF_10V", footprint="Capacitor_SMD:C_1206_3216Metric")
    c_out3 = SkidlPart("Device", "C_Polarized", ref="C_OUT3", value="470uF_16V", footprint="Capacitor_THT:CP_Radial_D10.0mm_P5.00mm")
    for c in (c_out1, c_out2, c_out3):
        c[1] += v5_bus
        c[2] += gnd

    d2 = SkidlPart("Device", "D_TVS", ref="D2", value="SMBJ5.8A", footprint="Diode_SMD:D_SMB")
    d2[1] += v5_bus
    d2[2] += gnd

    led2 = SkidlPart("Device", "LED", ref="LED2", value="5V_OK_GRN", footprint="LED_SMD:LED_0805_2012Metric")
    r_led2 = SkidlPart("Device", "R", ref="R_LED2", value="1.0k", footprint="Resistor_SMD:R_0805_2012Metric")
    led2[2] += v5_bus
    led2[1] += led5_k
    r_led2[1] += led5_k
    r_led2[2] += gnd

    # ==========================================================================
    # 4. 6x FUSED DC OUTPUT CHANNELS (3x 5V Left, 3x 12V Right)
    # ==========================================================================
    channels = [
        # (fuse_ref, fuse_val, conn_ref, conn_val, bus_net, out_net)
        ("F5", "2A_MINI", "J_5V_1",  "5V_HUE",     v5_bus,  v5_ch1),
        ("F6", "1A_MINI", "J_5V_2",  "5V_LUTRON",  v5_bus,  v5_ch2),
        ("F8", "2A_MINI", "J_5V_3",  "5V_AUX",     v5_bus,  v5_ch3),
        ("F7", "2A_MINI", "J_12V_3", "12V_AUX",    v12_bus, v12_ch3),
        ("F4", "2A_MINI", "J_12V_2", "12V_NETGEAR", v12_bus, v12_ch2),
        ("F3", "3A_MINI", "J_12V_1", "12V_ODROID", v12_bus, v12_ch1),
    ]
    for f_ref, f_val, j_ref, j_val, bus_net, out_net in channels:
        fuse = SkidlPart(
            "Device", "Fuse", ref=f_ref, value=f_val,
            footprint="Fuse:Fuseholder_Blade_Mini_Keystone_3568",
        )
        fuse[1] += bus_net
        fuse[2] += out_net

        conn = SkidlPart(
            "Connector_Generic", "Conn_01x02", ref=j_ref, value=j_val,
            footprint="TerminalBlock_Phoenix:TerminalBlock_Phoenix_PT-1,5-2-5.0-H_1x02_P5.00mm_Horizontal",
        )
        conn[1] += out_net
        conn[2] += gnd

    # ==========================================================================
    # 5. 6x M3 MECHANICAL MOUNTING HOLES (Non-Plated, Isolated)
    # ==========================================================================
    for i in range(1, 7):
        SkidlPart(
            "Mechanical", "MountingHole", ref=f"H{i}", value="M3",
            footprint="MountingHole:MountingHole_3.2mm_M3",
        )

    generate_pcb(file_=PCB_FILE, fp_libs=FP_LIBS)
    print(f"[SKiDL] Generated initial board: {PCB_FILE}")


def add_track(board, net, p1, p2, width_mm: float, layer=pcbnew.F_Cu) -> None:
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pt(*p1))
    t.SetEnd(pt(*p2))
    t.SetWidth(mm(width_mm))
    t.SetLayer(layer)
    t.SetNet(net)
    board.Add(t)


def add_poly_tracks(board, net, points, width_mm: float, layer=pcbnew.F_Cu) -> None:
    for a, b in zip(points, points[1:]):
        if abs(a[0] - b[0]) > 1e-4 or abs(a[1] - b[1]) > 1e-4:
            add_track(board, net, a, b, width_mm, layer)


def add_via(board, net, pos, size_mm: float = 1.0, drill_mm: float = 0.5) -> None:
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pt(*pos))
    v.SetWidth(mm(size_mm))
    v.SetDrill(mm(drill_mm))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetNet(net)
    board.Add(v)


def add_silk_text(board, text: str, pos, size_mm: float = 1.8, thickness_mm: float = 0.3,
                  layer=pcbnew.F_SilkS, horiz=pcbnew.GR_TEXT_H_ALIGN_CENTER) -> None:
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(pt(*pos))
    t.SetTextSize(pcbnew.VECTOR2I(mm(size_mm), mm(size_mm)))
    t.SetTextThickness(mm(thickness_mm))
    t.SetLayer(layer)
    t.SetHorizJustify(horiz)
    board.Add(t)


def add_line(board, p1, p2, width_mm: float = 0.25, layer=pcbnew.F_SilkS) -> None:
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pt(*p1))
    s.SetEnd(pt(*p2))
    s.SetWidth(mm(width_mm))
    s.SetLayer(layer)
    board.Add(s)


def pad_pos(fp, pad_num: str):
    """Return (x_mm, y_mm) of the first pad with the given number."""
    for p in fp.Pads():
        if p.GetNumber() == str(pad_num):
            pos = p.GetPosition()
            return (pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y))
    raise ValueError(f"Pad {pad_num} not found on {fp.GetReference()}")


def layout_and_route_pcb() -> None:
    board = pcbnew.LoadBoard(PCB_FILE)

    # --------------------------------------------------------------------------
    # 1. BOARD OUTLINE (196.0 x 90.0 mm)
    # --------------------------------------------------------------------------
    corners = [(0, 0), (BOARD_W, 0), (BOARD_W, BOARD_H), (0, BOARD_H)]
    for i in range(4):
        add_line(board, corners[i], corners[(i + 1) % 4], width_mm=0.15, layer=pcbnew.Edge_Cuts)

    # --------------------------------------------------------------------------
    # 2. DESIGN RULES (2 oz copper, safe mains clearances)
    # --------------------------------------------------------------------------
    ds = board.GetDesignSettings()
    ds.m_TrackMinWidth = mm(0.25)
    ds.m_ViasMinSize = mm(0.6)
    ds.m_ViasMinDrill = mm(0.3)
    ds.m_CopperEdgeClearance = mm(0.8)

    # --------------------------------------------------------------------------
    # 3. COMPONENT PLACEMENT
    # --------------------------------------------------------------------------
    placements = {
        # Mounting Holes (6x M3)
        "H1": (5.0, 5.0, 0),
        "H2": (98.0, 5.0, 0),
        "H3": (191.0, 5.0, 0),
        "H4": (5.0, 85.0, 0),
        "H5": (98.0, 85.0, 0),
        "H6": (191.0, 85.0, 0),

        # AC Mains Primary Zone (Left-Front, strictly isolated)
        "J_AC": (24.0, 8.0, 180),       # Pin1=AC_L at (24,8), Pin2=NC at (19,8), Pin3=AC_N at (14,8)
        "F_AC": (24.0, 20.0, 270),      # Pin1=AC_L at (24,20), Pin2=AC_L_FUSED at (24,30.16)
        "RV1":  (42.0, 16.0, 270),      # Pin1=AC_L_FUSED at (42,16), Pin2=AC_N at (42,23.5)

        # Mean Well IRM-60-12 (87.5 x 53.0 mm: X=[48.45, 135.95], Y=[10.30, 63.25])
        "U1":   (54.0, 16.0, 0),

        # 12V Primary Fuse, Bulk Cap, TVS, Power LED
        "F1":     (144.0, 52.0, 0),     # 4A Main 12V Fuse
        "C1":     (143.0, 38.0, 0),     # 470uF 25V Bulk Cap
        "C2":     (145.0, 29.0, 0),     # 100nF ceramic
        "D1":     (145.0, 22.0, 0),     # SMBJ15A TVS
        "LED1":   (143.0, 14.0, 180),   # 12V OK Green LED (Pin2=Anode Left, Pin1=Cathode Right)
        "R_LED1": (149.0, 14.0, 0),     # 2.2k

        # 12V -> 5V Synchronous Buck Converter (TI LMR33640ADDA, 4A)
        "F2":     (164.0, 52.0, 0),     # 2A Buck Input Fuse
        "U2":     (168.0, 26.0, 0),     # LMR33640ADDA HSOP-8-1EP
        "C_IN1":  (159.0, 24.0, 180),   # 22uF 25V 1206 (Pin1=VIN Right, Pin2=GND Left)
        "C_IN2":  (159.0, 28.0, 180),   # 10uF 25V 1206 (Pin1=VIN Right, Pin2=GND Left)
        "C_IN3":  (159.0, 20.0, 180),   # 100nF 25V 0805 (Pin1=VIN Right, Pin2=GND Left)
        "R_EN1":  (157.5, 33.0, 180),   # 100k UVLO top (Pin1=VIN Right, Pin2=EN Left)
        "R_EN2":  (157.5, 37.0, 0),     # 15k UVLO bot (Pin1=EN Left, Pin2=GND Right)
        "C_BOOT": (175.0, 24.5, 90),    # 100nF bootstrap
        "C_VCC":  (175.0, 29.5, 0),     # 1uF VCC LDO bypass
        "R_FB1":  (173.5, 34.0, 180),   # 100k 1% FB top (Pin2=FB Left, Pin1=5V Right)
        "R_FB2":  (173.5, 38.0, 0),     # 24.9k 1% FB bot (Pin1=FB Left, Pin2=GND Right)
        "C_FF":   (173.5, 42.0, 180),   # 22pF feedforward (Pin2=FB Left, Pin1=5V Right)
        "R_PG":   (166.5, 36.0, 180),   # 100k PG pullup (Pin2=PG Left, Pin1=5V Right)
        "L1":     (181.0, 16.0, 0),     # Bourns SRP1245A-100M (10uH, 8.5A)
        "C_OUT1": (185.0, 26.0, 0),     # 47uF 10V 1206 (Pin1=5V Left, Pin2=GND Right)
        "C_OUT2": (185.0, 30.0, 0),     # 47uF 10V 1206 (Pin1=5V Left, Pin2=GND Right)
        "C_OUT3": (183.5, 40.0, 0),     # 470uF 16V electrolytic (Pin1=5V Left, Pin2=GND Right)
        "D2":     (185.5, 49.0, 0),     # SMBJ5.8A TVS (Pin1=5V Left, Pin2=GND Right)
        "LED2":   (157.0, 12.0, 180),   # 5V OK Green LED (Pin2=Anode Left, Pin1=Cathode Right)
        "R_LED2": (163.0, 12.0, 0),     # 1.0k

        # Rear Distribution Row (aligned with 6 rear PDU bulkhead ports: X=18,50,82,114,146,178)
        "F5":      (13.0, 70.0, 0),     # 2A 5V Hue
        "J_5V_1":  (15.5, 83.0, 0),
        "F6":      (45.0, 70.0, 0),     # 1A 5V Lutron
        "J_5V_2":  (47.5, 83.0, 0),
        "F8":      (77.0, 70.0, 0),     # 2A 5V Aux
        "J_5V_3":  (79.5, 83.0, 0),
        "F7":      (109.0, 70.0, 0),    # 2A 12V Aux
        "J_12V_3": (111.5, 83.0, 0),
        "F4":      (141.0, 70.0, 0),    # 2A 12V Netgear
        "J_12V_2": (143.5, 83.0, 0),
        "F3":      (173.0, 70.0, 0),    # 3A 12V Odroid
        "J_12V_1": (175.5, 83.0, 0),
    }

    fps = {}
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        fps[ref] = fp
        if ref in placements:
            x, y, rot = placements[ref]
            fp.SetPosition(pt(x, y))
            fp.SetOrientationDegrees(rot)
            # Tidy reference/value silkscreen sizes
            fp.Reference().SetTextSize(pcbnew.VECTOR2I(mm(1.0), mm(1.0)))
            fp.Reference().SetTextThickness(mm(0.18))
            fp.Value().SetVisible(False)

    def net_by_name(name: str):
        return board.FindNet(name)

    # --------------------------------------------------------------------------
    # 4. ROUTING — IPC-2221 SIZED POWER & AC TRACES (2 oz Copper, dT < 10 C)
    # --------------------------------------------------------------------------
    # --- 4A. 120V AC MAINS (2.5 mm wide, >= 4 mm L-N clearance, >= 8 mm to DC) ---
    n_ac_l = net_by_name("AC_L")
    n_ac_lf = net_by_name("AC_L_FUSED")
    n_ac_n = net_by_name("AC_N")

    add_poly_tracks(board, n_ac_l, [
        pad_pos(fps["J_AC"], "1"),
        pad_pos(fps["F_AC"], "1"),
    ], width_mm=2.5, layer=pcbnew.F_Cu)

    add_poly_tracks(board, n_ac_lf, [
        pad_pos(fps["F_AC"], "2"),
        (36.0, 30.16),
        (36.0, 16.0),
        pad_pos(fps["RV1"], "1"),
        pad_pos(fps["U1"], "1"),
    ], width_mm=2.5, layer=pcbnew.F_Cu)

    # Route AC_N cleanly along the left side (X=11) below F_AC (Y=55) up to RV1 & U1 Pin 2
    add_poly_tracks(board, n_ac_n, [
        pad_pos(fps["J_AC"], "3"),
        (11.0, 8.0),
        (11.0, 56.0),
        (42.0, 56.0),
        pad_pos(fps["RV1"], "2"),
        (46.0, 23.5),
        (46.0, 22.75),
        pad_pos(fps["U1"], "2"),
    ], width_mm=2.5, layer=pcbnew.F_Cu)

    # --- 4B. TIE DUAL PADS ON EVERY KEYSTONE 3568 MINI-BLADE FUSE HOLDER ---
    for fref in ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8"):
        fp = fps[fref]
        for pnum in ("1", "2"):
            pts = [
                (pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y))
                for p in fp.Pads() if p.GetNumber() == pnum
            ]
            if len(pts) >= 2:
                p_net = next(p.GetNet() for p in fp.Pads() if p.GetNumber() == pnum)
                add_poly_tracks(board, p_net, pts, width_mm=2.5, layer=pcbnew.F_Cu)

    # --- 4B2. +12V_RAW (U1 Pin 3 -> F1 Pin 1, 4.0 mm wide, 5A+ capable) ---
    n_12raw = net_by_name("+12V_RAW")
    add_poly_tracks(board, n_12raw, [
        pad_pos(fps["U1"], "3"),
        (144.0, 57.25),
        pad_pos(fps["F1"], "1"),
    ], width_mm=4.0, layer=pcbnew.F_Cu)

    # --- 4C. +12V_BUS (4.0 mm main bus, connects F1 -> C1/C2/D1/LED1, F2, and F7/F4/F3) ---
    n_12bus = net_by_name("+12V_BUS")
    f1_p2 = pad_pos(fps["F1"], "2")
    f2_p1 = pad_pos(fps["F2"], "1")
    # F1 -> F2
    add_poly_tracks(board, n_12bus, [f1_p2, f2_p1], width_mm=3.0, layer=pcbnew.F_Cu)
    # F1 -> C1 -> C2 -> D1 -> LED1 (routed at Y=44 to keep >3mm clearance from +12V_BUCK_IN)
    add_poly_tracks(board, n_12bus, [
        f1_p2,
        (153.92, 43.5),
        (143.0, 43.5),
        pad_pos(fps["C1"], "1"),
        pad_pos(fps["C2"], "1"),
        pad_pos(fps["D1"], "1"),
        pad_pos(fps["LED1"], "2"),
    ], width_mm=2.0, layer=pcbnew.F_Cu)

    # Main 12V distribution bus bar on B.Cu at Y = 65.5 mm (4.0 mm wide!)
    # Fed by heavy via cluster at F1 Pin 2 (153.92, 58.0) -> B.Cu bus -> F7, F4, F3
    add_poly_tracks(board, n_12bus, [f1_p2, (153.92, 60.5)], width_mm=4.0, layer=pcbnew.F_Cu)
    for vx in (152.7, 153.9, 155.1):
        for vy in (59.5, 61.2):
            add_via(board, n_12bus, (vx, vy), size_mm=1.1, drill_mm=0.6)
    add_poly_tracks(board, n_12bus, [(153.92, 60.5), (153.92, 65.5)], width_mm=4.0, layer=pcbnew.B_Cu)
    add_poly_tracks(board, n_12bus, [(109.0, 65.5), (173.0, 65.5)], width_mm=4.0, layer=pcbnew.B_Cu)
    for fref in ("F7", "F4", "F3"):
        fp_p1 = pad_pos(fps[fref], "1")
        add_poly_tracks(board, n_12bus, [(fp_p1[0], 65.5), fp_p1], width_mm=3.0, layer=pcbnew.B_Cu)

    # --- 4D. +12V_BUCK_IN (F2 Pin 2 -> C_IN1/2/3, R_EN1, U2 Pin 2, 1.8 mm wide) ---
    n_12buck = net_by_name("+12V_BUCK_IN")
    add_poly_tracks(board, n_12buck, [
        pad_pos(fps["F2"], "2"),
        (173.92, 47.5),
        (161.6, 47.5),
        (161.6, 28.0),
        pad_pos(fps["C_IN2"], "1"),
        pad_pos(fps["C_IN1"], "1"),
        pad_pos(fps["C_IN3"], "1"),
    ], width_mm=1.8, layer=pcbnew.F_Cu)
    add_poly_tracks(board, n_12buck, [
        (161.6, 33.0),
        pad_pos(fps["R_EN1"], "1"),
    ], width_mm=0.5, layer=pcbnew.F_Cu)
    add_poly_tracks(board, n_12buck, [
        pad_pos(fps["C_IN1"], "1"),
        (162.8, 24.0),
        (162.8, 25.365),
        pad_pos(fps["U2"], "2"),
    ], width_mm=1.2, layer=pcbnew.F_Cu)

    # --- 4E. BUCK CONVERTER LOCAL ROUTING (LMR33640ADDA) ---
    # SW Node (thick, ultra-short low-EMI loop: U2 Pin 8 -> L1 Pin 1 & C_BOOT Pin 2)
    n_sw = net_by_name("BUCK_SW")
    u2_sw = pad_pos(fps["U2"], "8")
    l1_p1 = pad_pos(fps["L1"], "1")
    cboot_p2 = pad_pos(fps["C_BOOT"], "2")
    add_poly_tracks(board, n_sw, [u2_sw, (175.45, u2_sw[1]), l1_p1], width_mm=1.2, layer=pcbnew.F_Cu)
    add_poly_tracks(board, n_sw, [u2_sw, cboot_p2], width_mm=0.6, layer=pcbnew.F_Cu)

    # BOOT (U2 Pin 7 -> C_BOOT Pin 1)
    add_poly_tracks(board, net_by_name("BUCK_BOOT"), [
        pad_pos(fps["U2"], "7"),
        pad_pos(fps["C_BOOT"], "1"),
    ], width_mm=0.5, layer=pcbnew.F_Cu)

    # VCC (U2 Pin 6 -> C_VCC Pin 1)
    add_poly_tracks(board, net_by_name("BUCK_VCC"), [
        pad_pos(fps["U2"], "6"),
        (172.5, 26.635),
        (172.5, 29.5),
        pad_pos(fps["C_VCC"], "1"),
    ], width_mm=0.5, layer=pcbnew.F_Cu)

    # EN (R_EN2 Pin 1 -> R_EN1 Pin 2 -> short B.Cu bridge under +12V_BUCK_IN -> U2 Pin 3)
    n_en = net_by_name("BUCK_EN")
    ren1_p2 = pad_pos(fps["R_EN1"], "2")
    add_poly_tracks(board, n_en, [
        pad_pos(fps["R_EN2"], "1"),
        ren1_p2,
        (ren1_p2[0], 31.0),
    ], width_mm=0.4, layer=pcbnew.F_Cu)
    add_via(board, n_en, (ren1_p2[0], 31.0), size_mm=0.8, drill_mm=0.4)
    add_poly_tracks(board, n_en, [
        (ren1_p2[0], 31.0),
        (163.5, 31.0),
    ], width_mm=0.4, layer=pcbnew.B_Cu)
    add_via(board, n_en, (163.5, 31.0), size_mm=0.8, drill_mm=0.4)
    add_poly_tracks(board, n_en, [
        (163.5, 31.0),
        (163.5, 26.635),
        pad_pos(fps["U2"], "3"),
    ], width_mm=0.4, layer=pcbnew.F_Cu)

    # PG (U2 Pin 4 -> R_PG Pin 2)
    add_poly_tracks(board, net_by_name("BUCK_PG"), [
        pad_pos(fps["U2"], "4"),
        (164.5, 27.905),
        (164.5, 36.0),
        pad_pos(fps["R_PG"], "2"),
    ], width_mm=0.4, layer=pcbnew.F_Cu)

    # FB (U2 Pin 5 -> R_FB1 Pin 2, R_FB2 Pin 1, C_FF Pin 2)
    n_fb = net_by_name("BUCK_FB")
    add_poly_tracks(board, n_fb, [
        pad_pos(fps["U2"], "5"),
        (171.2, 27.905),
        (171.2, 34.0),
        pad_pos(fps["R_FB1"], "2"),
    ], width_mm=0.4, layer=pcbnew.F_Cu)
    add_poly_tracks(board, n_fb, [
        pad_pos(fps["R_FB1"], "2"),
        pad_pos(fps["R_FB2"], "1"),
        pad_pos(fps["C_FF"], "2"),
    ], width_mm=0.4, layer=pcbnew.F_Cu)

    # --- 4F. +5V_BUS (3.5 mm wide heavy power bus: L1 -> C_OUT1/2/3/D2 -> F8/F6/F5) ---
    n_5bus = net_by_name("+5V_BUS")
    l1_p2 = pad_pos(fps["L1"], "2")
    c_out1_p1 = pad_pos(fps["C_OUT1"], "1")
    c_out2_p1 = pad_pos(fps["C_OUT2"], "1")
    c_out3_p1 = pad_pos(fps["C_OUT3"], "1")
    d2_p1 = pad_pos(fps["D2"], "1")
    add_poly_tracks(board, n_5bus, [
        l1_p2,
        (l1_p2[0], 21.5),
        (c_out1_p1[0], 21.5),
        c_out1_p1,
        c_out2_p1,
        c_out3_p1,
        d2_p1,
    ], width_mm=2.5, layer=pcbnew.F_Cu)

    # Sense line from C_OUT3 back to R_FB1, C_FF, R_PG, LED2
    add_poly_tracks(board, n_5bus, [
        c_out3_p1,
        (178.0, 40.0),
        (178.0, 34.0),
        pad_pos(fps["R_FB1"], "1"),
    ], width_mm=0.5, layer=pcbnew.F_Cu)
    add_poly_tracks(board, n_5bus, [
        (178.0, 40.0),
        (178.0, 42.0),
        pad_pos(fps["C_FF"], "1"),
    ], width_mm=0.5, layer=pcbnew.F_Cu)
    add_poly_tracks(board, n_5bus, [
        (178.0, 42.0),
        (178.0, 44.5),
        (168.5, 44.5),
        (168.5, 36.0),
        pad_pos(fps["R_PG"], "1"),
    ], width_mm=0.4, layer=pcbnew.F_Cu)
    add_poly_tracks(board, n_5bus, [
        l1_p2,
        (l1_p2[0], 9.0),
        (155.5, 9.0),
        (155.5, 12.0),
        pad_pos(fps["LED2"], "2"),
    ], width_mm=0.6, layer=pcbnew.F_Cu)

    # Main +5V distribution bus bar along Y = 65.5 mm on F.Cu (3.5 mm wide!)
    add_poly_tracks(board, n_5bus, [
        d2_p1,
        (d2_p1[0], 65.5),
        (13.0, 65.5),
    ], width_mm=3.5, layer=pcbnew.F_Cu)
    for fref in ("F5", "F6", "F8"):
        fp_p1 = pad_pos(fps[fref], "1")
        add_poly_tracks(board, n_5bus, [(fp_p1[0], 65.5), fp_p1], width_mm=2.5, layer=pcbnew.F_Cu)

    # Indicator LED cathode -> resistor links
    add_poly_tracks(board, net_by_name("LED12_K"), [
        pad_pos(fps["LED1"], "1"),
        pad_pos(fps["R_LED1"], "1"),
    ], width_mm=0.4, layer=pcbnew.F_Cu)
    add_poly_tracks(board, net_by_name("LED5_K"), [
        pad_pos(fps["LED2"], "1"),
        pad_pos(fps["R_LED2"], "1"),
    ], width_mm=0.4, layer=pcbnew.F_Cu)

    # --- 4G. FUSED DC OUTPUT CHANNELS (2.5 mm for 3A Odroid, 2.0 mm for 1A-2A channels) ---
    out_routes = [
        ("F5", "J_5V_1",  "+5V_CH1_HUE",     2.0),
        ("F6", "J_5V_2",  "+5V_CH2_LUTRON",  2.0),
        ("F8", "J_5V_3",  "+5V_CH3_AUX",     2.0),
        ("F7", "J_12V_3", "+12V_CH3_AUX",    2.0),
        ("F4", "J_12V_2", "+12V_CH2_NETGEAR", 2.0),
        ("F3", "J_12V_1", "+12V_CH1_ODROID", 2.5),
    ]
    for fref, jref, nname, w_mm in out_routes:
        p_f = pad_pos(fps[fref], "2")
        p_j = pad_pos(fps[jref], "1")
        add_poly_tracks(board, net_by_name(nname), [
            p_f,
            (p_f[0], 77.5),
            (p_j[0], 77.5),
            p_j,
        ], width_mm=w_mm, layer=pcbnew.F_Cu)

    # --- 4H. GND STITCHING VIAS FOR SMD COMPONENTS ---
    n_gnd = net_by_name("GND")
    smd_gnd_vias = [
        ("C2", "2", 2.0, 0.0),
        ("D1", "2", 2.5, 0.0),
        ("R_LED1", "2", 2.0, 0.0),
        ("C_IN1", "2", -2.2, 0.0),
        ("C_IN2", "2", -2.2, 0.0),
        ("C_IN3", "2", -2.2, 0.0),
        ("R_EN2", "2", 0.0, 2.2),
        ("C_VCC", "2", 2.0, 0.0),
        ("R_FB2", "2", 2.0, 0.0),
        ("C_OUT1", "2", 2.2, 0.0),
        ("C_OUT2", "2", 2.2, 0.0),
        ("D2", "2", 2.5, 0.0),
        ("R_LED2", "2", 2.0, 0.0),
    ]
    for ref, pnum, dx, dy in smd_gnd_vias:
        p = pad_pos(fps[ref], pnum)
        vp = (p[0] + dx, p[1] + dy)
        add_poly_tracks(board, n_gnd, [p, vp], width_mm=0.8, layer=pcbnew.F_Cu)
        add_via(board, n_gnd, vp, size_mm=0.9, drill_mm=0.45)

    # Connect U2 Pin 1 (GND) directly to Pin 9 (thermal pad)
    add_poly_tracks(board, n_gnd, [
        pad_pos(fps["U2"], "1"),
        (168.0, 24.095),
        (168.0, 26.0),
    ], width_mm=0.6, layer=pcbnew.F_Cu)

    # Extra high-current GND stitching vias near U1 Pin 4, C1, C_OUT3, and rear terminals
    for gx, gy in [
        (134.0, 51.75), (134.0, 48.0), (134.0, 44.5),
        (168.0, 22.0), (168.0, 30.0),
        (190.5, 40.0), (190.5, 43.0),
    ]:
        add_via(board, n_gnd, (gx, gy), size_mm=1.1, drill_mm=0.6)

    # --------------------------------------------------------------------------
    # 5. SOLID SHARED GND COPPER PLANES (DC ZONE ONLY — STRICT AC ISOLATION!)
    # --------------------------------------------------------------------------
    # Polygon strictly excludes AC Primary Zone (X < 66, Y < 60)!
    # L-shaped DC zone polygon covers:
    #   - Right DC / Buck / PSU Secondary side: X in [66, 194.5], Y in [1.5, 88.5]
    #   - Rear 5V Distribution Strip:           X in [1.5, 66],   Y in [62.0, 88.5]
    dc_gnd_poly = [
        (66.0, 1.5),
        (194.5, 1.5),
        (194.5, 88.5),
        (1.5, 88.5),
        (1.5, 62.0),
        (66.0, 62.0),
    ]

    for layer in (pcbnew.B_Cu, pcbnew.F_Cu):
        zone = pcbnew.ZONE(board)
        zone.SetLayer(layer)
        zone.SetNet(n_gnd)
        zone.SetMinThickness(mm(0.3))
        zone.SetLocalClearance(mm(0.5))
        zone.SetThermalReliefGap(mm(0.5))
        zone.SetThermalReliefSpokeWidth(mm(0.8))
        zone.SetIsFilled(True)
        outline = zone.Outline()
        outline.NewOutline()
        for px, py in dc_gnd_poly:
            outline.Append(mm(px), mm(py))
        board.Add(zone)

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    # --------------------------------------------------------------------------
    # 6. SILKSCREEN LABELS, PORT MARKINGS & AC SAFETY BOUNDARY
    # --------------------------------------------------------------------------
    # Dashed/solid AC isolation boundary line on F.SilkS
    add_line(board, (62.0, 1.0), (62.0, 60.0), width_mm=0.35, layer=pcbnew.F_SilkS)
    add_line(board, (1.0, 60.0), (62.0, 60.0), width_mm=0.35, layer=pcbnew.F_SilkS)
    add_silk_text(board, "!! 120V AC MAINS !!", (45.0, 4.5), size_mm=1.35, thickness_mm=0.25)
    add_silk_text(board, "ISOLATION ZONE", (31.0, 58.2), size_mm=1.3, thickness_mm=0.25)

    # Board Title & Specs
    add_silk_text(board, "10-INCH 1U DC PDU - REV A (2oz Cu)", (98.0, 8.2), size_mm=1.6, thickness_mm=0.28)
    add_silk_text(board, "12V->5V 4A BUCK (LMR33640)", (168.0, 5.0), size_mm=1.3, thickness_mm=0.24)

    # Rear Output Port Labels (visible right above each fuse socket & terminal!)
    port_labels = [
        (18.0,  "5V-1 HUE (2A)"),
        (50.0,  "5V-2 LUTRON (1A)"),
        (82.0,  "5V-3 AUX (2A)"),
        (114.0, "12V-3 AUX (2A)"),
        (146.0, "12V-2 NETGEAR (2A)"),
        (178.0, "12V-1 ODROID (3A)"),
    ]
    for px, lbl in port_labels:
        add_silk_text(board, lbl, (px, 66.2), size_mm=1.1, thickness_mm=0.20)
        add_silk_text(board, "+   -", (px, 88.2), size_mm=1.1, thickness_mm=0.22)

    board.Save(PCB_FILE)
    print(f"[pcbnew] Saved routed PCB: {PCB_FILE}")


if __name__ == "__main__":
    generate_netlist_pcb()
    layout_and_route_pcb()
