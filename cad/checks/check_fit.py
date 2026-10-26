"""Geometry checks for the SmartPark Rev D enclosure.

Run with the project CAD environment:
    python cad/checks/check_fit.py

The sensor cans and display glass are simplified envelopes, not vendor CAD.
This script deliberately reports the HC-SR04 can pitch as unverified.
"""
from __future__ import annotations

import re
import hashlib
import json
import subprocess
import struct
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from cadgen import build123d as bd
from cadgen import read_step
from cadgen.geometry import boundary_edges, overlap_volume


CAD_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = CAD_ROOT.parent
SRC = CAD_ROOT / "src"
sys.path.insert(0, str(SRC))
import design as design  # noqa: E402

LIMIT_MM3 = 0.05
NATIVE_MANUFACTURING_PARTS = ("base", "lid", "front_oled")
results: list[tuple[str, str, str]] = []
_STORE_WHY_CACHE: dict[str, dict | Exception] = {}
_MANUFACTURING_MANIFEST_CACHE: dict | Exception | None = None


def report(name: str, status: str, detail: str) -> None:
    results.append((name, status, detail))


def manufacturing_freshness(path: Path, source_name: str) -> tuple[str, str]:
    """Verify native manufacturing outputs against every source/output SHA in the manifest."""
    global _MANUFACTURING_MANIFEST_CACHE
    manifest_path = CAD_ROOT / "checks" / "manufacturing-manifest.json"
    if _MANUFACTURING_MANIFEST_CACHE is None:
        try:
            _MANUFACTURING_MANIFEST_CACHE = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as exc:
            _MANUFACTURING_MANIFEST_CACHE = exc
    manifest = _MANUFACTURING_MANIFEST_CACHE
    if isinstance(manifest, Exception):
        return "UNVERIFIED", f"manufacturing manifest unavailable ({manifest!r})"

    part = manifest.get(source_name, {})
    hashes = part.get("sha256", {})
    expected_artifact = f"{path.parent.name}/{path.name}"
    required = {
        f"src/design.py",
        f"src/{source_name}.py",
        f"STEP/{source_name}.step",
        f"STL/{source_name}.stl",
        f"3MF/{source_name}.3mf",
    }
    missing_entries = sorted(required - set(hashes))
    if expected_artifact not in hashes or missing_entries:
        missing_entries = sorted(set(missing_entries) | ({expected_artifact} if expected_artifact not in hashes else set()))
        return "UNVERIFIED", "manifest missing required SHA-256 entries: " + ", ".join(missing_entries)

    mismatches = []
    missing = []
    for relative, expected in hashes.items():
        file_path = CAD_ROOT / Path(relative)
        if not file_path.is_file():
            missing.append(relative)
            continue
        actual = hashlib.sha256(file_path.read_bytes()).hexdigest()
        if actual.casefold() != str(expected).casefold():
            mismatches.append(relative)
    if mismatches:
        return "STALE", "manifest SHA-256 mismatch: " + ", ".join(mismatches)
    if missing:
        return "UNVERIFIED", "manifest inputs/outputs missing: " + ", ".join(missing)

    return "PASS", (
        f"native rebuild manifest SHA-256 values match for source, STEP, STL, and 3MF "
        f"({part.get('method', 'method unspecified')})"
    )


def artifact_freshness(path: Path, source_name: str) -> tuple[str, str]:
    """Use saved dependency/output hashes; timestamps are diagnostic only."""
    if source_name in NATIVE_MANUFACTURING_PARTS and path.suffix.casefold() in (".step", ".stl", ".3mf"):
        return manufacturing_freshness(path, source_name)

    source = f"src/{source_name}.py"
    if source not in _STORE_WHY_CACHE:
        try:
            completed = subprocess.run(
                [sys.executable, "-m", "cadgen.cli", "store", "why", source, "--json"],
                cwd=CAD_ROOT,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if not completed.stdout.strip():
                raise RuntimeError(
                    f"cadgen store why returned {completed.returncode} without JSON: {completed.stderr.strip()}"
                )
            # `store why` can exit nonzero when the model is stale while still
            # returning useful JSON with per-output hashes and stale reasons.
            _STORE_WHY_CACHE[source] = json.loads(completed.stdout)
        except Exception as exc:
            _STORE_WHY_CACHE[source] = exc

    record = _STORE_WHY_CACHE[source]
    if isinstance(record, Exception):
        newer = any(item.stat().st_mtime > path.stat().st_mtime for item in SRC.glob("*.py"))
        note = "source timestamps suggest newer edits" if newer else "timestamps show no newer source"
        return "UNVERIFIED", f"cadgen store metadata unavailable ({record!r}); {note}, timestamp is not proof"

    target = str(path.resolve()).casefold()
    outputs = record.get("clauses", [])
    for clause in outputs:
        for output in clause.get("outputs", []):
            output_path = str(output.get("path", "")).casefold()
            if output_path == target and isinstance(output.get("stale"), bool):
                output_stale = output["stale"]
                if output_stale:
                    return "STALE", "cadgen reports the saved output differs from its recorded hash"
                invalidating_clauses = [
                    c for c in record.get("clauses", [])
                    if c.get("stale") and c.get("clause") != 5
                ]
                if invalidating_clauses:
                    reason = next(
                        (c.get("why") for c in invalidating_clauses if c.get("why")),
                        "source/model dependency changed",
                    )
                    return "STALE", f"cadgen output hash matches, but model inputs are stale ({reason})"
                return "PASS", "cadgen confirms this output hash; model only has stale sibling outputs" if record.get("stale") else "cadgen model and this output report stale=false"

    # Some cadgen versions record only artifact hashes under record.outputs.
    # Without a stale bit for this exact output, do not infer freshness from mtimes.
    known_outputs = record.get("outputs", {})
    if any(str(output).casefold() == target for output in known_outputs):
        return "UNVERIFIED", "cadgen lists this output but provides no per-output freshness bit"
    stale = record.get("stale")
    if stale is True:
        return "STALE", "cadgen model metadata reports stale=true; artifact is not individually listed"
    return "UNVERIFIED", "cadgen metadata has no freshness result for this output"


def xyz(point) -> tuple[float, float, float]:
    return (float(point.X), float(point.Y), float(point.Z))


def bounds(shape) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    bb = shape.bounding_box()
    return xyz(bb.min), xyz(bb.max)


def validate_solid(name: str, shape) -> None:
    solids = shape.solids()
    valid = bool(shape.is_valid)
    free_edges = 0
    for solid in solids:
        for shell in solid.shells():
            free_edges += len(boundary_edges(shell))
    positive_volume = len(solids) > 0 and all(float(s.volume) > 0 for s in solids)
    one_closed_solid = len(solids) == 1 and free_edges == 0 and positive_volume and valid
    report(
        name,
        "PASS" if one_closed_solid else "FAIL",
        f"solids={len(solids)}, valid={valid}, free_shell_edges={free_edges}, "
        f"positive_volumes={positive_volume}",
    )


def overlap_sum(a, b) -> float:
    # Do not intersect moved assembly compounds directly: build123d 0.11.1
    # can traverse their children in the local frame. Query each placed solid.
    return sum(float(overlap_volume(sa, sb)) for sa in a.solids() for sb in b.solids())


def check_mechanical_electronics_clearances(
    mechanical_parts: list[tuple[str, object]],
    electronic_parts: list[tuple[str, object]],
) -> None:
    """Check every installed mechanical part against every electronics envelope."""
    checked = failures = errors = 0
    for mechanical_name, mechanical_shape in mechanical_parts:
        for electronic_name, electronic_shape in electronic_parts:
            try:
                volume = overlap_sum(mechanical_shape, electronic_shape)
            except Exception as exc:
                errors += 1
                report(
                    f"pair clearance/{mechanical_name} vs {electronic_name}",
                    "ERROR",
                    repr(exc),
                )
                continue
            checked += 1
            if volume > LIMIT_MM3:
                failures += 1
                report(
                    f"pair clearance/{mechanical_name} vs {electronic_name}",
                    "FAIL",
                    f"intersection={volume:.4f} mm^3; threshold={LIMIT_MM3:.3f} mm^3",
                )
    status = "ERROR" if errors else "FAIL" if failures else "PASS"
    report(
        "complete mechanical/electronics clearance matrix",
        status,
        f"checked {checked} shape pairs ({len(mechanical_parts)} mechanical × "
        f"{len(electronic_parts)} electronics); failures={failures}, errors={errors}; "
        f"overlap threshold={LIMIT_MM3:.3f} mm^3",
    )


def lid_clip_envelope():
    """Conservative four-clip envelope derived from the current lid parameters."""
    clip_t = float(design.CLIP_T)
    x_min = 32.1 - clip_t
    x_width = clip_t + 1.4  # includes the outboard angled tooth
    z_min = 26.4
    z_max = float(design.H) + 0.4
    clips = []
    for side in (-1, 1):
        for y in (-14, 14):
            envelope = design.box(x_min, y - 3.5, z_min, x_width, 7.0, z_max - z_min)
            if side < 0:
                envelope = bd.mirror(envelope, about=bd.Plane.YZ)
            clips.append(envelope)
    return bd.Compound(children=clips)


def _mesh_edge_key(point: tuple[float, float, float]) -> tuple[int, int, int]:
    # STL vertices are float32. Integer micrometres merge repeated triangle corners.
    return tuple(round(component * 1_000_000) for component in point)


def read_stl_topology(path: Path) -> dict:
    """Read binary/ASCII STL with stdlib and test edge incidence and signed volume."""
    data = path.read_bytes()
    triangles: list[tuple[tuple[float, float, float], ...]] = []
    binary_count = struct.unpack_from("<I", data, 80)[0] if len(data) >= 84 else -1
    if len(data) == 84 + 50 * binary_count:
        for i in range(binary_count):
            fields = struct.unpack_from("<12fH", data, 84 + i * 50)
            vertices = tuple(
                (float(fields[j]), float(fields[j + 1]), float(fields[j + 2]))
                for j in (3, 6, 9)
            )
            triangles.append(vertices)
    else:
        text = data.decode("ascii", errors="strict")
        vertices = [
            tuple(float(c) for c in match)
            for match in re.findall(
                r"vertex\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)",
                text,
                flags=re.IGNORECASE,
            )
        ]
        if not vertices or len(vertices) % 3:
            raise ValueError(f"{path.name}: unsupported/malformed STL")
        triangles = [tuple(vertices[i : i + 3]) for i in range(0, len(vertices), 3)]

    edge_counts: dict[tuple[tuple[int, int, int], tuple[int, int, int]], int] = {}
    points: list[tuple[float, float, float]] = []
    signed_volume = 0.0
    for tri in triangles:
        points.extend(tri)
        v0, v1, v2 = tri
        signed_volume += (
            v0[0] * (v1[1] * v2[2] - v1[2] * v2[1])
            + v0[1] * (v1[2] * v2[0] - v1[0] * v2[2])
            + v0[2] * (v1[0] * v2[1] - v1[1] * v2[0])
        ) / 6.0
        keys = [_mesh_edge_key(v) for v in tri]
        for p, q in ((keys[0], keys[1]), (keys[1], keys[2]), (keys[2], keys[0])):
            edge = (p, q) if p <= q else (q, p)
            edge_counts[edge] = edge_counts.get(edge, 0) + 1
    if not points:
        raise ValueError(f"{path.name}: STL has no triangles")
    counts = list(edge_counts.values())
    bad_edge_samples = [
        (
            edge_counts[edge],
            tuple(tuple(component / 1_000_000 for component in point) for point in edge),
        )
        for edge in edge_counts
        if edge_counts[edge] != 2
    ]
    min_xyz = tuple(min(p[i] for p in points) for i in range(3))
    max_xyz = tuple(max(p[i] for p in points) for i in range(3))
    return {
        "triangles": len(triangles),
        "watertight_edges": bool(counts) and all(n == 2 for n in counts),
        "bad_edges": sum(n != 2 for n in counts),
        "bad_edge_samples": bad_edge_samples,
        "signed_volume_mm3": signed_volume,
        "bounds": (min_xyz, max_xyz),
    }


def read_3mf_topology(path: Path) -> dict:
    """Read one indexed 3MF triangle mesh and check its declared length unit and edge manifoldness."""
    with zipfile.ZipFile(path) as package:
        model_path = "3D/3dmodel.model"
        if model_path not in package.namelist():
            raise ValueError(f"{path.name}: missing {model_path}")
        root = ET.fromstring(package.read(model_path))

    namespace = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
    meshes = []
    for obj in root.findall(".//m:object", namespace):
        mesh = obj.find("m:mesh", namespace)
        if mesh is None:
            continue
        vertices = [
            (float(v.attrib["x"]), float(v.attrib["y"]), float(v.attrib["z"]))
            for v in mesh.findall("m:vertices/m:vertex", namespace)
        ]
        triangles = [
            (int(t.attrib["v1"]), int(t.attrib["v2"]), int(t.attrib["v3"]))
            for t in mesh.findall("m:triangles/m:triangle", namespace)
        ]
        meshes.append((vertices, triangles))
    if len(meshes) != 1:
        raise ValueError(f"{path.name}: expected one indexed mesh, found {len(meshes)}")
    vertices, triangles = meshes[0]
    if not vertices or not triangles:
        raise ValueError(f"{path.name}: mesh has no vertices or triangles")

    edge_counts: dict[tuple[int, int], int] = {}
    signed_volume = 0.0
    for tri in triangles:
        if any(index < 0 or index >= len(vertices) for index in tri):
            raise ValueError(f"{path.name}: triangle index outside vertex array")
        v0, v1, v2 = (vertices[i] for i in tri)
        signed_volume += (
            v0[0] * (v1[1] * v2[2] - v1[2] * v2[1])
            + v0[1] * (v1[2] * v2[0] - v1[0] * v2[2])
            + v0[2] * (v1[0] * v2[1] - v1[1] * v2[0])
        ) / 6.0
        for p, q in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            edge = (p, q) if p <= q else (q, p)
            edge_counts[edge] = edge_counts.get(edge, 0) + 1

    low = tuple(min(vertex[i] for vertex in vertices) for i in range(3))
    high = tuple(max(vertex[i] for vertex in vertices) for i in range(3))
    counts = list(edge_counts.values())
    return {
        "unit": root.attrib.get("unit", "millimeter"),
        "triangles": len(triangles),
        "bad_edges": sum(count != 2 for count in counts),
        "watertight_edges": bool(counts) and all(count == 2 for count in counts),
        "signed_volume_mm3": signed_volume,
        "bounds": (low, high),
        "mesh_count": len(meshes),
    }


def check_print_3mf(name: str) -> None:
    path = CAD_ROOT / "3MF" / f"{name}.3mf"
    if not path.exists():
        report(f"3MF/{name}", "PENDING", "saved 3MF not present")
        return
    try:
        mesh = read_3mf_topology(path)
        low, high = mesh["bounds"]
        unit_ok = mesh["unit"] == "millimeter"
        at_z0 = abs(low[2]) <= 0.03
        closed = mesh["watertight_edges"]
        positive = mesh["signed_volume_mm3"] > 0
        passed = unit_ok and at_z0 and closed and positive
        report(
            f"3MF/{name}",
            "PASS" if passed else "FAIL",
            f"unit={mesh['unit']}, meshes={mesh['mesh_count']}, triangles={mesh['triangles']}, "
            f"watertight_edges={closed}, bad_edges={mesh['bad_edges']}, "
            f"signed_volume={mesh['signed_volume_mm3']:.2f} mm^3, "
            f"Z=[{low[2]:.6f},{high[2]:.6f}] mm",
        )
        freshness_status, freshness_detail = artifact_freshness(path, name)
        report(f"3MF/{name} freshness", freshness_status, freshness_detail)
    except Exception as exc:
        report(f"3MF/{name}", "ERROR", repr(exc))


def check_print_stl(name: str) -> None:
    path = CAD_ROOT / "STL" / f"{name}.stl"
    if not path.exists():
        report(f"STL/{name}", "PENDING", "saved STL not present")
        return
    try:
        mesh = read_stl_topology(path)
    except Exception as exc:
        report(f"STL/{name}", "ERROR", repr(exc))
        return
    low, high = mesh["bounds"]
    at_z0 = abs(low[2]) <= 0.03
    closed = mesh["watertight_edges"]
    positive = mesh["signed_volume_mm3"] > 0
    passed = at_z0 and closed and positive
    mesh_status = "PASS" if passed else "FAIL"
    freshness_status, freshness_detail = artifact_freshness(path, name)
    edge_detail = "; bad-edge samples=" + ", ".join(
        f"{count}×{a}->{b}" for count, (a, b) in mesh["bad_edge_samples"]
    ) if mesh["bad_edge_samples"] else ""
    report(
        f"STL/{name}",
        mesh_status,
        f"triangles={mesh['triangles']}, watertight_edges={closed}, "
        f"bad_edges={mesh['bad_edges']}, signed_volume={mesh['signed_volume_mm3']:.2f} mm^3, "
        f"Z=[{low[2]:.4f},{high[2]:.4f}] mm{edge_detail}",
    )
    report(f"STL/{name} freshness", freshness_status, freshness_detail)


def add_saved_step_checks() -> None:
    for name in (
        "base",
        "lid",
        "sensor_mask",
        "sensor_retainer",
        "front_oled",
        "front_blank",
        "oled_retainer",
        "light_pipe",
        "fit_coupon",
    ):
        path = CAD_ROOT / "STEP" / f"{name}.step"
        if not path.exists():
            report(f"STEP/{name}", "PENDING", "saved STEP not present")
            continue
        shape = read_step(path)
        freshness_status, freshness_detail = artifact_freshness(path, name)
        validate_solid(f"STEP/{name}", shape)
        report(f"STEP/{name} freshness", freshness_status, freshness_detail)
        low, high = bounds(shape)
        if abs(low[2]) <= 0.03:
            z_status = "PASS"
            detail = f"saved print pose has Z bound [{low[2]:.3f}, {high[2]:.3f}] mm"
        else:
            z_status = "FAIL"
            detail = f"saved print pose is not placed on Z=0: [{low[2]:.3f}, {high[2]:.3f}] mm"
        report(f"STEP/{name} print origin", z_status, detail)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    # Construct each native source part once; these are the installed poses.
    base = design.base_shape()
    lid = design.lid_shape()
    mask = design.mask_shape()
    sensor_retainer = design.sensor_retainer_shape()
    panel = design.panel_shape(oled=True)
    blank_panel = design.panel_shape(oled=False)
    oled_retainer = design.oled_retainer_shape()
    electronics = design.electronics_shape(oled=True)
    clip_envelope = lid_clip_envelope()
    children = {child.label: child for child in electronics.children}
    stack_for_pair_check = None
    header_keepout = children.get("OLED header/cable keepout")
    interface_path = PROJECT_ROOT / "docs" / "mechanical-interface.json"
    interface_cfg = (
        json.loads(interface_path.read_text(encoding="utf-8"))
        if interface_path.exists()
        else {}
    )

    for name, shape in (
        ("source base", base),
        ("source lid", lid),
        ("source acoustic mask", mask),
        ("source sensor retainer", sensor_retainer),
        ("source OLED panel", panel),
        ("source blank panel", blank_panel),
        ("source OLED retainer", oled_retainer),
    ):
        validate_solid(name, shape)

    for name, shape in (
        ("source base", base),
        ("source lid", lid),
        ("source acoustic mask", mask),
        ("source sensor retainer", sensor_retainer),
        ("source OLED panel", panel),
        ("source blank panel", blank_panel),
        ("source OLED retainer", oled_retainer),
    ):
        pose_name = {
            "source lid": "lid",
            "source OLED panel": "front_oled",
            "source blank panel": "front_blank",
            "source OLED retainer": "oled_retainer",
            "source sensor retainer": "sensor_retainer",
        }.get(name, "")
        print_shape = design.print_pose(shape, pose_name)
        low, high = bounds(print_shape)
        aligned = abs(low[2]) <= 0.03
        report(
            f"{name} print orientation",
            "PASS" if aligned else "FAIL",
            f"Z=[{low[2]:.3f},{high[2]:.3f}] mm",
        )

    try:
        volume = overlap_sum(base, lid)
        report(
            "base/lid installed interference",
            "PASS" if volume <= LIMIT_MM3 else "FAIL",
            f"intersection={volume:.4f} mm^3; threshold={LIMIT_MM3:.3f} mm^3",
        )
    except Exception as exc:
        report("base/lid installed interference", "ERROR", repr(exc))

    # The mask's frame seats in two stepped openings in the bottom shell.
    mask_clear_x = (56.4 - 56.0) / 2
    mask_clear_y = (26.4 - 26.0) / 2
    try:
        volume = overlap_sum(base, mask)
        seated = mask_clear_x >= 0 and mask_clear_y >= 0 and volume <= LIMIT_MM3
        report(
            "mask-to-shell nominal seat",
            "PASS" if seated else "FAIL",
            f"frame/opening clearance={mask_clear_x:.2f} mm per X side, "
            f"{mask_clear_y:.2f} mm per Y side; overlap={volume:.4f} mm^3",
        )
    except Exception as exc:
        report("mask-to-shell nominal seat", "ERROR", repr(exc))

    # The nominal can geometry is only a drawing-free placeholder; do not report this as a vendor-fit pass.
    can_diameter_mm = 16.0
    can_pitch_mm = float(design.CAN_PITCH)
    aperture_mm = 17.0
    radial_clearance = (aperture_mm - can_diameter_mm) / 2
    report(
        "HC-SR04 can-to-mask interface",
        "UNVERIFIED",
        f"model assumes can OD {can_diameter_mm:.1f} mm, pitch {can_pitch_mm:.1f} mm, "
        f"and mask hole {aperture_mm:.1f} mm (radial clearance {radial_clearance:.2f} mm); "
        "module source drawing does not dimension actual can OD/pitch; verify the purchased sensor physically.",
    )
    for label in ("HC-SR04 transducer 1", "HC-SR04 transducer 2"):
        can = children.get(label)
        if can is None:
            report(f"mask clearance/{label}", "PENDING", "reference can envelope not found")
            continue
        try:
            volume = overlap_sum(mask, can)
            report(
                f"mask clearance/{label}",
                "INFO" if volume <= LIMIT_MM3 else "FAIL",
                f"surrogate intersection={volume:.4f} mm^3; this only checks the modeled 16 mm can at assumed 26 mm pitch",
            )
        except Exception as exc:
            report(f"mask clearance/{label}", "ERROR", repr(exc))

    sensor_board = children.get("HC-SR04 PCB reference")
    if sensor_board is not None:
        try:
            retainer_overlap = overlap_sum(sensor_retainer, sensor_board)
            case_overlap = overlap_sum(base, sensor_board)
            report(
                "sensor PCB/retainer and shell contact",
                "PASS" if max(retainer_overlap, case_overlap) <= LIMIT_MM3 else "FAIL",
                f"retainer intersection={retainer_overlap:.4f} mm^3; shell intersection={case_overlap:.4f} mm^3",
            )
        except Exception as exc:
            report("sensor PCB/retainer and shell contact", "ERROR", repr(exc))

    battery = children.get("Protected LiPo 51x34x5 reference")
    if battery is not None:
        try:
            battery_base_overlap = overlap_sum(base, battery)
            x_side = (52.0 - 51.0) / 2
            y_side = (35.0 - 34.0) / 2
            report(
                "battery envelope vs tray",
                "PASS" if battery_base_overlap <= LIMIT_MM3 else "FAIL",
                f"overlap={battery_base_overlap:.4f} mm^3; nominal side clearances "
                f"X={x_side:.2f} mm, Y={y_side:.2f} mm. Verify actual pack and foam; "
                "side fit is tolerance-sensitive and is not a swelling allowance.",
            )
            low, high = bounds(battery)
            base_floor_z = 2.4
            board_z = float(design.PCB_Z)
            vertical_gap = board_z - (high[2])
            report(
                "battery vertical envelope",
                "INFO",
                f"pouch reference Z=[{low[2]:.2f},{high[2]:.2f}] mm; "
                f"floor-to-pouch-bottom={low[2]-base_floor_z:.2f} mm; "
                f"pouch-top to carrier reference plane={vertical_gap:.2f} mm. "
                "Flexible strap is not a rigid squeeze cap; actual pack, lead and cell expansion behavior still require inspection.",
            )
        except Exception as exc:
            report("battery envelope vs tray", "ERROR", repr(exc))

    # electronics_shape requires the actual carrier STEP; never score a placeholder.
    pcb_path = design.PCB_STEP
    try:
        pcb = electronics.children[0]
        pcb_label = pcb.label or f"actual carrier PCB STEP ({pcb_path.name})"
        overlap_base = overlap_sum(base, pcb)
        overlap_lid = overlap_sum(lid, pcb)
        report(
            "carrier-to-shell clearance",
            "PASS" if max(overlap_base, overlap_lid) <= LIMIT_MM3 else "FAIL",
            f"source carrier={pcb_label}; base overlap={overlap_base:.4f} mm^3; "
            f"lid overlap={overlap_lid:.4f} mm^3",
        )
        clip_overlap = overlap_sum(clip_envelope, pcb)
        clip_low, _ = bounds(clip_envelope)
        _, board_high = bounds(pcb)
        clip_gap = clip_low[2] - board_high[2]
        report(
            "lid clip envelope vs actual carrier STEP",
            "PASS" if clip_overlap <= LIMIT_MM3 else "FAIL",
            f"clip starts at Z={clip_low[2]:.2f} mm; carrier top Z={board_high[2]:.2f} mm; "
            f"vertical separation={clip_gap:.2f} mm; overlap={clip_overlap:.4f} mm^3",
        )
        if battery is not None:
            board_low, _ = bounds(pcb)
            _, battery_high = bounds(battery)
            gap = board_low[2] - battery_high[2]
            report(
                "carrier-to-battery vertical clearance",
                "PASS" if gap > 0 else "FAIL",
                f"gap={gap:.3f} mm (carrier lower face minus pouch reference top)",
            )
        for label in ('HC-SR04 PCB reference','HC-SR04 right-angle harness envelope','GoldenMorning OLED PCB reference','OLED header/cable keepout'):
            module=children.get(label)
            if module is not None:
                volume=overlap_sum(pcb,module)
                report(f'carrier vs {label}','PASS' if volume<=LIMIT_MM3 else 'FAIL',f'intersection={volume:.4f} mm^3')
    except Exception as exc:
        report("carrier-to-shell clearance", "ERROR", repr(exc))

    # An independently imported XIAO/Wio stack needs an explicit, saved placement.
    stack_path = CAD_ROOT / "imported" / "xiao-s3-wio-sx1262-stack.step"
    if not stack_path.exists():
        report("XIAO/Wio stack STEP clearance", "PENDING", "imported aligned stack STEP not present")
    elif not interface_path.exists():
        raw_stack = read_step(stack_path)
        low, high = bounds(raw_stack)
        report(
            "XIAO/Wio stack STEP clearance",
            "PENDING",
            f"STEP exists with raw bbox X[{low[0]:.3f},{high[0]:.3f}], "
            f"Y[{low[1]:.3f},{high[1]:.3f}], Z[{low[2]:.3f},{high[2]:.3f}] mm, "
            f"but {interface_path} with its case transform is not present.",
        )
    else:
        try:
            cfg = interface_cfg
            stack_cfg = cfg.get("stack", {})
            translation = cfg.get(
                "stack_to_case",
                stack_cfg.get("case_translation", cfg.get("step_to_case")),
            )
            rotation = cfg.get(
                "stack_rotation",
                stack_cfg.get("rotation", cfg.get("step_rotation", [0, 0, 0])),
            )
            if translation is None:
                report(
                    "XIAO/Wio stack STEP clearance",
                    "PENDING",
                    "mechanical interface file has no stack_to_case/step_to_case placement",
                )
            else:
                stack = read_step(stack_path).moved(
                    bd.Location(tuple(translation), tuple(rotation))
                )
                # Flatten after placement. Check that leaf-world bounds preserve the
                # positioned STEP envelope before using solid-wise boolean checks.
                stack = bd.Compound(children=list(stack.solids()))
                stack_for_pair_check = stack
                low, high = bounds(stack)
                pose_error = max(
                    abs(low[i] - (-8.89005, 3.7801, 31.2397+design.COPPER_SEAT_LIFT+design.XIAO_HEADER_AIR_GAP)[i])
                    for i in range(3)
                )
                pose_error = max(
                    pose_error,
                    *(
                        abs(high[i] - (8.89005, 26.5045, 43.0+design.COPPER_SEAT_LIFT+design.XIAO_HEADER_AIR_GAP)[i])
                        for i in range(3)
                    ),
                )
                report(
                    "XIAO/Wio STEP global-leaf placement",
                    "PASS" if pose_error <= 0.03 else "FAIL",
                    f"flattened leaf bounds X[{low[0]:.3f},{high[0]:.3f}], "
                    f"Y[{low[1]:.3f},{high[1]:.3f}], Z[{low[2]:.3f},{high[2]:.3f}] mm; "
                    f"max deviation from configured placement={pose_error:.4f} mm",
                )
                for index,header in enumerate(electronics.children):
                    if 'header body reference' in header.label or 'header shoulder reference' in header.label:
                        volume=overlap_sum(stack,header)
                        report(f'XIAO/Wio vs header {index} ({header.label})','PASS' if volume<=LIMIT_MM3 else 'FAIL',f'intersection={volume:.4f} mm^3; housing must clear component-face parts')
                base_overlap = overlap_sum(base, stack)
                lid_overlap = overlap_sum(lid, stack)
                clip_stack_overlap = overlap_sum(clip_envelope, stack)
                battery_overlap = 0.0 if battery is None else overlap_sum(battery, stack)
                panel_overlap = overlap_sum(panel, stack)
                oled_retainer_overlap = overlap_sum(oled_retainer, stack)
                report(
                    "XIAO/Wio stack shell/battery clearance",
                    "PASS" if max(base_overlap, lid_overlap, battery_overlap, panel_overlap, oled_retainer_overlap) <= LIMIT_MM3 else "FAIL",
                    f"case-transformed bbox X[{low[0]:.2f},{high[0]:.2f}], "
                    f"Y[{low[1]:.2f},{high[1]:.2f}], Z[{low[2]:.2f},{high[2]:.2f}] mm; "
                    f"base overlap={base_overlap:.4f}, lid overlap={lid_overlap:.4f}, "
                    f"battery overlap={battery_overlap:.4f}, OLED panel overlap={panel_overlap:.4f}, "
                    f"OLED retainer overlap={oled_retainer_overlap:.4f} mm^3",
                )
                report(
                    "lid clip envelope vs XIAO/Wio component stack",
                    "PASS" if clip_stack_overlap <= LIMIT_MM3 else "FAIL",
                    f"stack bbox X[{low[0]:.2f},{high[0]:.2f}], Z[{low[2]:.2f},{high[2]:.2f}] mm; "
                    f"clip-to-stack overlap={clip_stack_overlap:.4f} mm^3",
                )
                if header_keepout is not None:
                    stack_header_overlap = overlap_sum(stack, header_keepout)
                    report(
                        "XIAO/Wio stack vs OLED harness keepout",
                        "PASS" if stack_header_overlap <= LIMIT_MM3 else "FAIL",
                        f"intersection={stack_header_overlap:.4f} mm^3",
                    )
        except Exception as exc:
            report("XIAO/Wio stack STEP clearance", "ERROR", repr(exc))

    electronic_parts = [
        (
            child.label or (
                "actual carrier PCB STEP" if index == 0
                else f"electronics reference {index + 1}"
            ),
            child,
        )
        for index, child in enumerate(electronics.children)
    ]
    if stack_for_pair_check is not None:
        electronic_parts.append(("XIAO/Wio imported stack", stack_for_pair_check))
    common_electronics = [
        (name, shape)
        for name, shape in electronic_parts
        if name not in {
            "GoldenMorning OLED PCB reference",
            "OLED glass reference",
            "OLED active-area reference",
            "OLED header/cable keepout",
        }
    ]
    check_mechanical_electronics_clearances(
        [
            ("base", base),
            ("lid", lid),
            ("acoustic mask", mask),
            ("sensor retainer", sensor_retainer),
            ("OLED panel", panel),
            ("OLED retainer", oled_retainer),
            ("status light pipe", design.light_pipe_shape()),
        ],
        electronic_parts,
    )
    check_mechanical_electronics_clearances(
        [
            ("base", base),
            ("lid", lid),
            ("acoustic mask", mask),
            ("sensor retainer", sensor_retainer),
            ("blank panel", blank_panel),
            ("status light pipe", design.light_pipe_shape()),
        ],
        common_electronics,
    )

    # Printed front panel is a separate, screw-mounted component; it must not penetrate the shell.
    for name, separate_panel in (("OLED panel", panel), ("blank panel", blank_panel)):
        try:
            volume = overlap_sum(base, separate_panel)
            report(
                f"base/{name} installed fit",
                "PASS" if volume <= LIMIT_MM3 else "FAIL",
                f"intersection={volume:.4f} mm^3; threshold={LIMIT_MM3:.3f} mm^3",
            )
        except Exception as exc:
            report(f"base/{name} installed fit", "ERROR", repr(exc))

    # Panel opening against the manufacturer active/viewing-area dimensions.
    active_clear_x = (24.4 - 21.744) / 2
    active_clear_z = (13.5 - 10.864) / 2
    view_clear_x = (24.4 - 23.744) / 2
    view_clear_z = (13.5 - 12.864) / 2
    display_contains = active_clear_x >= 0 and active_clear_z >= 0
    report(
        "OLED window vs drawing active area",
        "PASS" if display_contains else "FAIL",
        f"window {24.4:.1f} × {13.5:.1f} mm; active-area nominal border "
        f"X={active_clear_x:.3f} mm, Z={active_clear_z:.3f} mm; "
        f"viewing-area border X={view_clear_x:.3f} mm, Z={view_clear_z:.3f} mm. "
        "Verify the supplier module and panel opening registration before fabrication.",
    )

    module = children.get("GoldenMorning OLED PCB reference")
    glass = children.get("OLED glass reference")
    active = children.get("OLED active-area reference")
    header_keepout = children.get("OLED header/cable keepout")
    if module is not None:
        low, high = bounds(module)
        dimensions = tuple(round(high[i] - low[i], 3) for i in range(3))
        report(
            "OLED module modeled envelope",
            "INFO",
            f"source envelope dimensions X/Y/Z={dimensions}; supplier PCB is 27.8 × 27.5 × 1.2 mm, "
            "so treat the source's Y thickness/connector envelope as a keepout, not vendor PCB geometry.",
        )
    for name, moving in (
        ("OLED glass", glass),
        ("OLED active area", active),
        ("OLED module", module),
    ):
        if moving is None:
            report(f"panel clearance/{name}", "PENDING", "reference geometry not found")
            continue
        try:
            volume = overlap_sum(panel, moving)
            report(
                f"panel clearance/{name}",
                "PASS" if volume <= LIMIT_MM3 else "FAIL",
                f"intersection={volume:.4f} mm^3; window/cavity should leave this envelope unobstructed",
            )
        except Exception as exc:
            report(f"panel clearance/{name}", "ERROR", repr(exc))
    if header_keepout is not None:
        for name, fixed in (
            ("base", base),
            ("lid", lid),
            ("OLED retainer", oled_retainer),
            ("OLED panel", panel),
        ):
            try:
                volume = overlap_sum(fixed, header_keepout)
                report(
                    f"OLED harness keepout/{name}",
                    "PASS" if volume <= LIMIT_MM3 else "FAIL",
                    f"intersection={volume:.4f} mm^3",
                )
            except Exception as exc:
                report(f"OLED harness keepout/{name}", "ERROR", repr(exc))

    # Four M4 mount bores are modeled as vertical 4.5 mm through-holes.
    blocked = []
    for side in (-1, 1):
        for y in (-21, 21):
            bore = design.cyl(side * 41, y, 0, 4.5, 60)
            blocked.append(overlap_sum(base, bore))
    max_block = max(blocked, default=0.0)
    report(
        "mounting-ear M4 bore clearance",
        "PASS" if max_block <= LIMIT_MM3 else "FAIL",
        f"maximum base-solid intersection across four Ø4.5 mm bores={max_block:.4f} mm^3",
    )

    # Planned right-side bulkhead hole, axis normal to the X+ wall.
    antenna_cfg = interface_cfg.get("antenna", {})
    bore_d = float(antenna_cfg.get("bore", 6.6))
    center_y, center_z = antenna_cfg.get("center_yz", [0, 40])
    if antenna_cfg.get("bulkhead_axis", "X").upper() != "X":
        report("SMA bulkhead path", "PENDING", "checker currently expects the specified bulkhead axis to be X")
    else:
        coax_probe = bd.Pos(design.W / 2 - 5, center_y, center_z) * bd.Rot(0, 90, 0) * bd.Cylinder(
            bore_d / 2, 10, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
        )
        try:
            coax_blockage = overlap_sum(base, coax_probe)
            report(
                f"SMA bulkhead Ø{bore_d:.1f} mm path",
                "PASS" if coax_blockage <= LIMIT_MM3 else "FAIL",
                f"probe axis along X at y={center_y},z={center_z}; "
                f"base-solid intersection={coax_blockage:.4f} mm^3",
            )
        except Exception as exc:
            report("SMA bulkhead path", "ERROR", repr(exc))

    # Match the source's clip thickness and hook-root reference length.
    clip_thickness = float(design.CLIP_T)
    hook_low = 28.0 + float(design.D) + float(design.HOOK_SHIFT)
    hook_high = 30.4 + float(design.D) + float(design.HOOK_SHIFT)
    hook_root_length = float(design.H) + 0.4 - hook_high
    window_low = 27.7 + float(design.D) + float(design.HOOK_SHIFT)
    window_high = window_low + 3.0
    hook_z_clearances = (hook_low - window_low, window_high - hook_high)
    free_beam_span = float(design.H) + 0.4 - 26.4
    strains = {
        delta: 1.5 * clip_thickness * delta / (hook_root_length**2)
        for delta in (0.4, 0.6, 0.8, 1.0, 1.4)
    }
    report(
        "latch-window registration / beam estimate",
        "INFO",
        f"Current source gives window 3.7 × 8.2 × 3.0 mm at Z={window_low:.1f}..{window_high:.1f} "
        f"and tooth 1.4 × 7.0 × 2.4 mm at Z={hook_low:.1f}..{hook_high:.1f}; "
        f"Y edge clearance 0.60 mm, lower/upper Z clearances {hook_z_clearances[0]:.2f}/{hook_z_clearances[1]:.2f} mm. "
        f"Clip thickness CLIP_T={clip_thickness:.1f} mm; full free span={free_beam_span:.1f} mm; "
        f"hook-root length H+.4-(30.4+D+HOOK_SHIFT)={hook_root_length:.1f} mm. "
        "Cantilever strain estimate ε≈1.5·t·δ/L² (not FEA): "
        + ", ".join(f"δ={d:.1f} mm → {100*e:.3f}%" for d, e in strains.items())
        + ". Actual required deflection, print material/orientation, fatigue and latch force are unverified.",
    )

    add_saved_step_checks()
    for printable in (
        "base",
        "lid",
        "sensor_mask",
        "sensor_retainer",
        "front_oled",
        "front_blank",
        "oled_retainer",
        "light_pipe",
        "fit_coupon",
    ):
        check_print_stl(printable)
        check_print_3mf(printable)

    failures = sum(status in ("FAIL", "ERROR") for _, status, _ in results)
    print("SmartPark Rev D fit check (millimetres; overlap threshold %.3f mm^3)" % LIMIT_MM3)
    print("=" * 88)
    for name, status, detail in results:
        print(f"{status:10} {name}: {detail}")
    print("=" * 88)
    print(f"checks={len(results)} failures={failures} "
          f"unverified={sum(status in ('UNVERIFIED', 'PENDING', 'STALE') for _, status, _ in results)}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
