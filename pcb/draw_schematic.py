"""
Generate a clean vector circuit schematic (SVG) for the 10-Inch 1U DC PDU Prototype PCB
using schemdraw.
"""

from pathlib import Path
import schemdraw
import schemdraw.elements as elm

OUT_SVG = str(Path(__file__).resolve().parent / "pdu_schematic.svg")


def draw_schematic() -> None:
    with schemdraw.Drawing(file=OUT_SVG, show=False, font="sans-serif", fontsize=10) as d:
        d.config(unit=2.6)

        # ======================================================================
        # 1. AC MAINS PRIMARY INPUT (120V AC -> IRM-60-12)
        # ======================================================================
        d += elm.Label().at((0, 10.6)).label("120V AC PRIMARY (ISOLATED ZONE)", halign="left", fontsize=11, color="#b91c1c")

        # J_AC Live & Neutral
        ac_l_in = d.add(elm.Dot(open=True).at((0, 9.2)).label("J_AC:1\nAC_L (120V)", loc="left"))
        d += elm.FuseIEC().right().at(ac_l_in.end).label("F_AC\n2A-T 250V\n(Bulgin FX0457)", loc="top")
        mov_top = d.add(elm.Dot())
        d += elm.Line().right(1.8)
        u1_in_l = d.here

        ac_n_in = d.add(elm.Dot(open=True).at((0, 6.8)).label("J_AC:3\nAC_N", loc="left"))
        d += elm.Line().right(mov_top.end[0] - ac_n_in.end[0])
        mov_bot = d.add(elm.Dot())
        d += elm.ResistorVar().up().at(mov_bot.end).to(mov_top.end).label("RV1\nS14K150\nMOV", loc="right")
        d += elm.Line().right(1.8).at(mov_bot.end)

        # U1: Mean Well IRM-60-12 (4kVAC Class II)
        u1 = d.add(
            elm.Ic(
                pins=[
                    elm.IcPin(name="AC/L", pin="1", side="left", slot="3/4"),
                    elm.IcPin(name="AC/N", pin="2", side="left", slot="1/4"),
                    elm.IcPin(name="+12V", pin="3", side="right", slot="3/4"),
                    elm.IcPin(name="GND",  pin="4", side="right", slot="1/4"),
                ],
                size=(4.6, 3.6),
                edgepadH=0.4,
            ).anchor("AC/L").at(u1_in_l).label("U1: Mean Well\nIRM-60-12\n(12V 5A / 60W\nClass II 4kVAC)", loc="top", fontsize=9)
        )

        # ======================================================================
        # 2. +12V PRIMARY RAIL, F1 MAIN FUSE, BULK FILTERING & TVS
        # ======================================================================
        d += elm.Label().at((10.5, 10.6)).label("+12V PRIMARY RAIL (4.0mm 2oz Cu)", halign="left", fontsize=11, color="#1d4ed8")

        d += elm.FuseIEC().right().at(u1.absanchors["+12V"]).label("F1\n4A MINI\n(Main 12V)", loc="top")
        bus12_n1 = d.add(elm.Dot())

        # Shared GND reference from U1 Pin 4
        d += elm.Line().right(1.2).at(u1.absanchors["GND"])
        d += elm.Ground()

        # Bulk Cap C1 + Ceramic C2 + TVS D1
        d += elm.Capacitor2(polar=True).down(2.2).at(bus12_n1.end).label("C1\n470uF 25V", loc="bottom")
        d += elm.Ground()

        d += elm.Line().right(2.0).at(bus12_n1.end)
        bus12_n2 = d.add(elm.Dot())
        d += elm.Zener().up(2.2).at((bus12_n2.end[0], bus12_n2.end[1] - 2.2)).label("D1\nSMBJ15A", loc="bottom")
        d += elm.Ground().at((bus12_n2.end[0], bus12_n2.end[1] - 2.2))

        # +12V_BUS Rail Stub -> goes to Buck F2 and to 12V Output Channels
        d += elm.Line().right(2.2).at(bus12_n2.end)
        bus12_split = d.add(elm.Dot().label("+12V_BUS", loc="top", color="#1d4ed8"))

        # ======================================================================
        # 3. 12V -> 5V 4A SYNCHRONOUS BUCK CONVERTER (TI LMR33640ADDA)
        # ======================================================================
        d += elm.Label().at((18.0, 10.6)).label("12V -> 5V 4A SYNCHRONOUS BUCK", halign="left", fontsize=11, color="#047857")

        d += elm.FuseIEC().right().at(bus12_split.end).label("F2\n2A MINI\n(Buck In)", loc="top")
        buck_vin = d.add(elm.Dot())
        d += elm.Capacitor().down(2.0).at(buck_vin.end).label("C_IN1..3\n22u+10u\n+100n", loc="bottom")
        d += elm.Ground()

        d += elm.Line().right(1.4).at(buck_vin.end)
        u2 = d.add(
            elm.Ic(
                pins=[
                    elm.IcPin(name="VIN",  pin="2", side="left", slot="3/4"),
                    elm.IcPin(name="EN",   pin="3", side="left", slot="1/4"),
                    elm.IcPin(name="SW",   pin="8", side="right", slot="3/4"),
                    elm.IcPin(name="FB",   pin="5", side="right", slot="1/4"),
                    elm.IcPin(name="GND",  pin="1,9", side="bot", slot="1/2"),
                ],
                size=(4.2, 3.2),
                edgepadH=0.35,
            ).anchor("VIN").label("U2: TI LMR33640ADDA\n(4A, 400kHz Sync Buck)", loc="top", fontsize=9)
        )
        d += elm.Ground().at(u2.absanchors["GND"])

        # EN UVLO pullup note
        d += elm.Resistor().left(1.2).at(u2.absanchors["EN"]).label("R_EN1/2\n9.3V UVLO", loc="bottom", fontsize=8)

        # SW -> L1 (10uH 8.5A) -> +5V_BUS
        d += elm.Inductor2(loops=4).right(2.8).at(u2.absanchors["SW"]).label("L1\n10uH 8.5A\n(SRP1245A)", loc="top")
        bus5_n1 = d.add(elm.Dot().label("+5V_BUS (3.5mm 2oz)", loc="top", color="#047857"))

        # Output Caps C_OUT1..3 & SMBJ5.8A TVS
        d += elm.Capacitor2(polar=True).down(2.2).at(bus5_n1.end).label("C_OUT1..3\n2x47uF +\n470uF", loc="bottom")
        d += elm.Ground()

        d += elm.Line().right(2.0).at(bus5_n1.end)
        bus5_n2 = d.add(elm.Dot())
        d += elm.Resistor().down(1.6).at(bus5_n2.end).label("R_FB1\n100k 1%", loc="right", fontsize=8)
        fb_mid = d.add(elm.Dot())
        d += elm.Resistor().down(1.6).at(fb_mid.end).label("R_FB2\n24.9k 1%", loc="right", fontsize=8)
        d += elm.Ground()
        # FB line back to U2 FB
        d += elm.Line().left().at(fb_mid.end).tox(u2.absanchors["FB"]).toy(u2.absanchors["FB"])

        # ======================================================================
        # 4. REAR FUSED DC DISTRIBUTION CHANNELS (6x Phoenix PT-1,5 Terminals)
        # ======================================================================
        d += elm.Label().at((0, 3.6)).label("FUSED DC OUTPUT DISTRIBUTION (6x Keystone 3568 Mini-Blade Sockets -> 6x Phoenix 5.0mm Terminals)", halign="left", fontsize=11, color="#111827")

        channels = [
            ("F5: 2A", "J_5V_1\n5V Hue",      "+5V_BUS",  "#047857", 0.5),
            ("F6: 1A", "J_5V_2\n5V Lutron",   "+5V_BUS",  "#047857", 5.8),
            ("F8: 2A", "J_5V_3\n5V Aux",      "+5V_BUS",  "#047857", 11.1),
            ("F7: 2A", "J_12V_3\n12V Aux",    "+12V_BUS", "#1d4ed8", 16.8),
            ("F4: 2A", "J_12V_2\n12V Netgear","+12V_BUS", "#1d4ed8", 22.1),
            ("F3: 3A", "J_12V_1\n12V Odroid", "+12V_BUS", "#1d4ed8", 27.4),
        ]

        for f_lbl, j_lbl, rail_lbl, col, x0 in channels:
            src = d.add(elm.Dot().at((x0, 2.2)).label(rail_lbl, loc="top", color=col, fontsize=8))
            d += elm.FuseIEC().right(2.0).at(src.end).label(f_lbl, loc="top", fontsize=8.5)
            d += elm.Dot(open=True).label(j_lbl + "\n(+ / GND)", loc="right", fontsize=8.5)
            d += elm.Ground().at((x0 + 2.0, 0.9))

    print(f"[schemdraw] Saved schematic: {OUT_SVG}")


if __name__ == "__main__":
    draw_schematic()
