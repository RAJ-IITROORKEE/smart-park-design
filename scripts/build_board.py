"""Build the revision-d KiCad carrier PCB from the checked schematic netlist."""

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
KICAD_FOOTPRINTS = Path(r"C:\Users\rajra\.codex\pcb-toolchain\kicad\share\kicad\footprints")
NETLIST = ROOT / "hardware" / "SmartMark.net"
BOARD = ROOT / "hardware" / "SmartMark.kicad_pcb"
DSN = ROOT / "hardware" / "SmartMark.dsn"
SES = ROOT / "hardware" / "SmartMark.ses"
PROJECT = ROOT / "hardware" / "SmartMark.kicad_pro"
PLACEMENTS = {
    # Socket origin is the mechanical center of the XIAO carrier interface.
    "U1": (31.0, 10.5, 0),
    "J1": (28.0, 46.0, 0),
    "J2": (59.0, 33.0, 0),
    "U2": (47.0, 29.0, 0),
    "L1": (50.5, 29.0, 180),
    "C1": (47.0, 25.4, 270),
    "C2": (42.0, 29.0, 180),
    "C3": (53.0, 36.5, 90),
    "C4": (19.0, 35.5, 0),
    "C5": (54.0, 19.8, 0),
    "C6": (50.1, 19.5, 0),
    "C7": (59.2, 27.2, 0),
    "U3": (52.0, 22.5, 0),
    "U4": (20.5, 39.0, 0),
    "R1": (44.5, 32.0, 0),
    "R2": (47.5, 32.0, 0),
    "R3": (49.5, 35.5, 0),
    "R4": (24.0, 39.0, 90),
    "R5": (56.5, 22.5, 0),
    "R6": (57.5, 26.5, 0),
    "R7": (47.5, 21.5, 0),
    "R8": (51.0, 42.0, 90),
    "R9": (54.0, 42.0, 90),
    "TP1": (4.0, 35.0, 0),
    "TP2": (7.0, 35.0, 0),
    "TP3": (58.5, 29.0, 0),
    "TP4": (17.0, 39.0, 0),
    "TP5": (12.0, 35.5, 0),
    # Bottom-side emitter over the case light-pipe axis; its electrical pads are
    # assigned from the schematic after the footprint is flipped to B.Cu.
    "D1": (60.0, 25.0, 0),
}
MOUNTING_HOLES = [(2.5, 3.0), (59.5, 3.0), (2.5, 47.0), (59.5, 47.0)]
FOOTPRINT_CACHE: dict[str, pcbnew.FOOTPRINT] = {}


def mm(value: float) -> int:
    return pcbnew.FromMM(value)


def v2(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(mm(x), mm(y))


def load_footprint(lib_id: str) -> pcbnew.FOOTPRINT:
    library, name = lib_id.split(":", 1)
    cached = FOOTPRINT_CACHE.get(lib_id)
    if cached is not None:
        footprint = pcbnew.FOOTPRINT(cached)
    else:
        folder = ROOT / "hardware" / f"{library}.pretty" if library == "SmartMark" else KICAD_FOOTPRINTS / f"{library}.pretty"
        source = pcbnew.FootprintLoad(str(folder), name)
        if source is None:
            raise RuntimeError(f"Cannot load footprint {lib_id} from {folder}")
        FOOTPRINT_CACHE[lib_id] = pcbnew.FOOTPRINT(source)
        footprint = pcbnew.FOOTPRINT(source)

    footprint.SetFPID(pcbnew.LIB_ID(library, name))

    # KiCad's footprint copy constructor preserves child UUIDs. Reset every
    # instance UUID before adding it to a board so repeated package types do not
    # create phantom shorts or courtyard collisions in DRC.
    footprint.ResetUuid()
    footprint.Reference().ResetUuid()
    footprint.Value().ResetUuid()
    for item in footprint.GraphicalItems():
        item.ResetUuid()
    for pad in footprint.Pads():
        pad.ResetUuid()
    return footprint


def assert_unique_uuids(board: pcbnew.BOARD) -> None:
    seen: dict[str, str] = {}

    def claim(item: object, label: str) -> None:
        uuid = item.m_Uuid.AsString()
        if uuid in seen:
            raise AssertionError(f"Duplicate KiCad UUID {uuid}: {seen[uuid]} and {label}")
        seen[uuid] = label

    for footprint in board.GetFootprints():
        ref = footprint.GetReference()
        claim(footprint, f"footprint {ref}")
        claim(footprint.Reference(), f"reference {ref}")
        claim(footprint.Value(), f"value {ref}")
        for item in footprint.GraphicalItems():
            claim(item, f"graphic {ref}")
        for pad in footprint.Pads():
            claim(pad, f"pad {ref}.{pad.GetNumber()}")
    for item in board.GetDrawings():
        claim(item, f"drawing {item.GetClass()}")


def set_router_netclasses() -> None:
    text = DSN.read_text(encoding="utf-8")
    pattern = r"    \(class kicad_default .*?    \)\n  \)\n  \(wiring"
    replacement = """    (class kicad_default /BOOST_FB /BOOST_SW /LED_DATA_5V BOOST_EN
      ECHO_GPIO HC_ECHO HC_TRIG I2C_SCL I2C_SDA LED_DATA_3V3 LED_DIN
      (circuit
        (use_via \"Via[0-1]_600:300_um\")
      )
      (rule
        (width 250)
        (clearance 200)
      )
    )
    (class kicad_power 3V3 5V_SENSOR GND
      (circuit
        (use_via \"Via[0-1]_600:300_um\")
      )
      (rule
        (width 300)
        (clearance 200)
      )
    )
  )
  (wiring"""
    text, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError("Could not assign 0.25 mm signal and 0.3 mm power routing classes in DSN")
    # The router's board-level default also needs the signal width, not the
    # 0.2 mm minimum width emitted by the KiCad DSN exporter.
    text = text.replace("(width 200)", "(width 250)", 1)
    DSN.write_text(text, encoding="utf-8")


def add_edge(board: pcbnew.BOARD, start: tuple[float, float], end: tuple[float, float]) -> None:
    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.SHAPE_T_SEGMENT)
    shape.SetStart(v2(*start))
    shape.SetEnd(v2(*end))
    shape.SetLayer(pcbnew.Edge_Cuts)
    shape.SetWidth(mm(0.05))
    board.Add(shape)


def add_board_text(board: pcbnew.BOARD, text: str, x: float, y: float, size: float = 1.0) -> None:
    item = pcbnew.PCB_TEXT(board)
    item.SetText(text)
    item.SetPosition(v2(x, y))
    item.SetLayer(pcbnew.F_SilkS)
    item.SetTextSize(v2(size, size))
    item.SetTextThickness(mm(0.15))
    board.Add(item)


def write_project_settings() -> None:
    rules = {
        "min_clearance": 0.2,
        "min_track_width": 0.18,
        "min_via_diameter": 0.6,
        "min_through_hole_diameter": 0.3,
        "min_copper_edge_clearance": 0.25,
    }
    classes = [
        {"name": "Default", "clearance": 0.2, "track_width": 0.25, "via_diameter": 0.6, "via_drill": 0.3},
        {"name": "Power", "clearance": 0.2, "track_width": 0.3, "via_diameter": 0.6, "via_drill": 0.3},
    ]
    patterns = [{"netclass": "Power", "pattern": net} for net in ("3V3", "5V_SENSOR", "GND")]
    PROJECT.write_text(json.dumps({
        "meta": {"filename": "SmartMark.kicad_pro", "version": 1},
        "board": {"design_settings": {"rules": rules}},
        "net_settings": {"meta": {"version": 3}, "classes": classes, "netclass_patterns": patterns},
    }, indent=2) + "\n", encoding="utf-8")


def add_ground_zones(board: pcbnew.BOARD) -> None:
    gnd = board.FindNet("GND")
    if gnd is None:
        raise RuntimeError("GND net missing from board")
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        zone = pcbnew.ZONE(board)
        zone.SetLayer(layer)
        zone.SetNetCode(gnd.GetNetCode())
        zone.SetLocalClearance(mm(0.2))
        zone.SetThermalReliefGap(mm(0.25))
        zone.SetThermalReliefSpokeWidth(mm(0.3))
        zone.SetMinThickness(mm(0.2))
        outline = zone.Outline()
        outline.NewOutline()
        for x, y in ((0.5, 0.5), (61.5, 0.5), (61.5, 49.5), (0.5, 49.5)):
            outline.Append(mm(x), mm(y))
        board.Add(zone)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())


ENVELOPE_MODELS = {
    "C2": "C_1206_3216Metric_envelope.step",
    "C3": "C_1206_3216Metric_envelope.step",
    "U2": "WSON-6-1EP_2x2mm_envelope.step",
    "U3": "SOT-23-6_envelope.step",
    "U4": "SOT-23-5_envelope.step",
    "L1": "VLS3012CX_2R2M_envelope.step",
    "D1": "WS2812B_2020_V6_envelope.step",
    "J2": "PinHeader_1x04_P2.54mm_Vertical_envelope.step",
}


def set_envelope_model(footprint: pcbnew.FOOTPRINT, ref: str) -> None:
    filename = ENVELOPE_MODELS.get(ref)
    if not filename:
        return
    model_path = f"${{KIPRJMOD}}/SmartMark.pretty/3dmodels/{filename}"
    models = footprint.Models()
    if models:
        if len(models) != 1:
            raise RuntimeError(f"Expected at most one 3D model on {ref}, found {len(models)}")
        model = models[0]
        model.m_Filename = model_path
    else:
        model = pcbnew.FP_3DMODEL()
        model.m_Filename = model_path
        model.m_Offset = pcbnew.VECTOR3D(0.0, 0.0, 0.0)
        model.m_Rotation = pcbnew.VECTOR3D(0.0, 0.0, 0.0)
        model.m_Scale = pcbnew.VECTOR3D(1.0, 1.0, 1.0)
        model.m_Show = True
        footprint.Add3DModel(model)
    if ref == "J2":
        # Pin 1 is the native KiCad footprint origin; center the envelope's
        # four positions on the row while keeping pin 1 at the board origin.
        model.m_Offset = pcbnew.VECTOR3D(0.0, -3.81, 0.0)


def build() -> dict[str, object]:
    if not NETLIST.exists():
        raise FileNotFoundError(f"Missing KiCad-exported netlist: {NETLIST}; export from the current schematic first")
    root = ET.parse(NETLIST).getroot()
    components_node = root.find("components")
    nets_node = root.find("nets")
    if components_node is None or nets_node is None:
        raise ValueError("KiCad netlist has no components/nets section")
    all_components = {item.attrib["ref"]: item for item in components_node}
    components = {ref: item for ref, item in all_components.items() if item.findtext("footprint", "").strip()}
    off_board_refs = sorted(set(all_components) - set(components))
    if set(components) != set(PLACEMENTS):
        raise ValueError(f"Placement map and schematic differ; missing={sorted(set(components) - set(PLACEMENTS))}, extra={sorted(set(PLACEMENTS) - set(components))}")
    if off_board_refs != ["BT1", "J3", "J4"]:
        raise ValueError(f"Expected only the declared battery harness parts off-board; found {off_board_refs}")

    board = pcbnew.BOARD()
    write_project_settings()
    board.GetTitleBlock().SetTitle("SmartMark Revision D Carrier")
    board.GetTitleBlock().SetRevision("D-pilot")
    board.GetDesignSettings().SetCopperLayerCount(2)
    try:
        board.GetDesignSettings().SetBoardThickness(mm(1.6))
    except AttributeError:
        pass

    add_edge(board, (0, 0), (62, 0))
    add_edge(board, (62, 0), (62, 50))
    add_edge(board, (62, 50), (0, 50))
    add_edge(board, (0, 50), (0, 0))

    add_board_text(board, "SMARTMARK REV D", 53.0, 7.0, 1.1)
    add_board_text(board, "5V USB-C INPUT ONLY", 14.0, 43.0, 0.8)
    add_board_text(board, "SOLAR MUST BE REGULATED", 14.0, 46.0, 0.8)

    net_nodes: dict[tuple[str, str], str] = {}
    net_names: list[str] = []
    for net in nets_node:
        name = net.attrib["name"]
        if name.startswith("unconnected-"):
            name = name.replace("/", "{slash}")
        board_nodes = [node for node in net.findall("node") if node.attrib["ref"] in components]
        if not board_nodes:
            continue
        net_names.append(name)
        for node in board_nodes:
            net_nodes[(node.attrib["ref"], node.attrib["pin"])] = name
    nets: dict[str, pcbnew.NETINFO_ITEM] = {}
    for code, name in enumerate(net_names, start=1):
        item = pcbnew.NETINFO_ITEM(board, name, code)
        board.Add(item)
        nets[name] = item

    for ref, component in components.items():
        lib_id = component.findtext("footprint", "")
        footprint = load_footprint(lib_id)
        footprint.SetReference(ref)
        footprint.SetValue(component.findtext("value", ""))
        if ref.startswith("TP"):
            footprint.SetExcludedFromBOM(False)
        x, y, angle = PLACEMENTS[ref]
        footprint.SetPosition(v2(x, y))
        footprint.SetOrientationDegrees(angle)
        set_envelope_model(footprint, ref)
        board.Add(footprint)
        if ref in {"D1", "C7"}:
            footprint.SetLayerAndFlip(pcbnew.B_Cu)
        if ref == "D1":
            expected = {"1": (-0.915, 0.55), "2": (-0.915, -0.55), "3": (0.915, -0.55), "4": (0.915, 0.55)}
            actual = {pad.GetNumber(): ((pad.GetPosition().x - footprint.GetPosition().x) / 1_000_000, (pad.GetPosition().y - footprint.GetPosition().y) / 1_000_000) for pad in footprint.Pads()}
            for number, (x, y) in expected.items():
                ax, ay = actual[number]
                if abs(ax - x) > 0.01 or abs(ay - y) > 0.01:
                    raise AssertionError(f"D1 B.Cu pad {number} is at {(ax, ay)}, expected {expected[number]} in carrier-top view")
        for pad in footprint.Pads():
            name = net_nodes.get((ref, pad.GetNumber()))
            if name:
                pad.SetNet(nets[name])
        # The module stack covers U1's reference area, so keep its assembly
        # label on F.Fab and reserve silkscreen for board-level instructions.
        reference = footprint.Reference()
        if ref == "U1":
            reference.SetLayer(pcbnew.F_Fab)
            reference.SetPosition(v2(x, 0.8))
            reference.SetTextSize(v2(1.0, 1.0))
            reference.SetTextThickness(mm(0.15))
        else:
            reference.SetLayer(pcbnew.B_Fab if ref in {"D1", "C7"} else pcbnew.F_Fab)
            reference.SetPosition(v2(x, y - 1.6))
            reference.SetTextSize(v2(0.8, 0.8))
            reference.SetTextThickness(mm(0.12))
        footprint.Value().SetVisible(False)

    hole_fp = pcbnew.FootprintLoad(str(KICAD_FOOTPRINTS / "MountingHole.pretty"), "MountingHole_2.7mm")
    if hole_fp is None:
        raise RuntimeError("Cannot load MountingHole:MountingHole_2.7mm")
    for idx, (x, y) in enumerate(MOUNTING_HOLES, start=1):
        hole = pcbnew.FOOTPRINT(hole_fp)
        hole.SetFPID(pcbnew.LIB_ID("MountingHole", "MountingHole_2.7mm"))
        hole.SetBoardOnly(True)
        hole.ResetUuid()
        hole.Reference().ResetUuid()
        hole.Value().ResetUuid()
        for item in hole.GraphicalItems():
            item.ResetUuid()
        for pad in hole.Pads():
            pad.ResetUuid()
        hole.SetReference(f"H{idx}")
        hole.SetValue("M2.5")
        hole.SetPosition(v2(x, y))
        hole.Reference().SetVisible(False)
        hole.Value().SetVisible(False)
        board.Add(hole)

    assert_unique_uuids(board)
    pcbnew.SaveBoard(str(BOARD), board)
    reloaded = pcbnew.LoadBoard(str(BOARD))
    assert_unique_uuids(reloaded)
    if not pcbnew.ExportSpecctraDSN(board, str(DSN)):
        raise RuntimeError(f"Failed to export DSN to {DSN}")
    set_router_netclasses()
    return {
        "board": str(BOARD),
        "dsn": str(DSN),
        "boardMm": [62, 50, 1.6],
        "mountingHolesMm": MOUNTING_HOLES,
        "components": len(components),
        "offBoardParts": off_board_refs,
        "nets": len(nets),
        "unconnectedPads": sum(1 for fp in board.GetFootprints() for pad in fp.Pads() if pad.GetNetCode() == 0),
        "tracks": sum(1 for item in board.GetTracks()),
        "placementNote": "Placement follows the verified XIAO component-side-down mirror. D1 and C7 are on B.Cu; component clearance envelopes are documented separately.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=ROOT / "verification" / "board-placement.json")
    parser.add_argument("--finish", action="store_true", help="import the Freerouting session and fill ground planes")
    args = parser.parse_args()
    if args.finish:
        board = pcbnew.LoadBoard(str(BOARD))
        if not SES.exists() or not pcbnew.ImportSpecctraSES(board, str(SES)):
            raise RuntimeError(f"Cannot import the Freerouting session {SES}")
        add_ground_zones(board)
        pcbnew.SaveBoard(str(BOARD), board)
        report = {"board": str(BOARD), "dsn": str(DSN), "ses": str(SES), "tracks": sum(1 for item in board.GetTracks()), "vias": sum(1 for item in board.GetTracks() if isinstance(item, pcbnew.PCB_VIA)), "finish": "Freerouting session imported; F.Cu and B.Cu GND zones filled."}
    else:
        report = build()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
