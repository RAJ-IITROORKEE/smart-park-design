"""Export compact STEP envelopes for packages missing from the local KiCad model set.

These are dimensional clearance envelopes, not vendor cosmetic CAD. See
docs/3D_MODELS.md for dimensions and provenance before using them for fit checks.
"""

from pathlib import Path

from build123d import Align, Box, Compound, export_step


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hardware" / "SmartMark.pretty" / "3dmodels"


def box(x: float, y: float, z: float, *, zmin: float = 0.0) -> Box:
    return Box(x, y, z, align=(Align.CENTER, Align.CENTER, Align.MIN)).translate((0, 0, zmin))


def export(name: str, shape: object) -> None:
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    export_step(shape, str(path))
    if not path.exists() or path.stat().st_size < 500:
        raise RuntimeError(f"STEP export failed: {path}")
    print(f"{path.name}: {path.stat().st_size} bytes")


def main() -> None:
    # Worldsemi package clearance envelope, 2.1 x 2.1 x 0.90 mm. Optical window
    # is not modeled as an opaque cosmetic detail; the outer body bounds the
    # case light-pipe clearance requirement.
    export("WS2812B_2020_V6_envelope.step", box(2.1, 2.1, 0.90))

    # Conservative TI DBV clearance cube including lead span: 3.1 x 3.1 x 1.45 mm.
    export("SOT-23-5_envelope.step", box(3.1, 3.1, 1.45))
    export("SOT-23-6_envelope.step", box(3.1, 3.1, 1.45))

    # Conservative TI DRV WSON-6 clearance envelope: 2.1 x 2.1 x 0.8 mm. The center thermal pad
    # and leads are represented by the footprint copper, not duplicated here.
    export("WSON-6-1EP_2x2mm_envelope.step", box(2.1, 2.1, 0.8))

    # Conservative Murata GRM31 1206 case maximum: 3.4 x 1.8 x 1.8 mm.
    export("C_1206_3216Metric_envelope.step", box(3.4, 1.8, 1.8))

    # Conservative TDK VLS3012CX case maximum: 3.2 x 3.2 x 1.3 mm.
    export("VLS3012CX_2R2M_envelope.step", box(3.2, 3.2, 1.3))

    # Generic 1x4 2.54 mm vertical header. Body 2.54 x 10.16 x 2.5 mm;
    # square 0.64 mm pins extend 3.5 mm below and 6.0 mm above the board plane.
    housing = box(2.54, 10.16, 2.5)
    pins = [box(0.64, 0.64, 9.5, zmin=-3.5).translate((0, y, 0)) for y in (-3.81, -1.27, 1.27, 3.81)]
    export("PinHeader_1x04_P2.54mm_Vertical_envelope.step", Compound(children=[housing, *pins]))


if __name__ == "__main__":
    main()
