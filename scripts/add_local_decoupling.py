"""Add schematic instances for RGB rail decoupling capacitors C6 and C7."""

from __future__ import annotations

import re
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMATIC = ROOT / "hardware" / "SmartMark.kicad_sch"
SHEET_UUID = "674f78dd-d1d7-5d8b-a372-ff50be24fdff"
NAMESPACE = uuid.UUID("4dd4c6d2-8e3a-4d52-a6c3-360b0998d241")
PLACEMENTS = {"C6": (198.12, 224.79), "C7": (223.52, 144.78)}


def uuid_for(key: str) -> str:
    return str(uuid.uuid5(NAMESPACE, key))


def block_for_ref(text: str, ref: str) -> str:
    marker = f'(property "Reference" "{ref}"'
    ref_at = text.index(marker)
    start = text.rfind("\n\t(symbol", 0, ref_at) + 1
    if start <= 0:
        raise ValueError(f"Could not locate symbol block for {ref}")
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        c = text[i]
        if in_string:
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == '"':
                in_string = False
            continue
        if c == '"':
            in_string = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    raise ValueError(f"Unclosed symbol block for {ref}")


def clone_symbol(block: str, old_ref: str, new_ref: str, dx: float, dy: float) -> str:
    block = re.sub(
        r'\(at (-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?) (-?\d+)\)',
        lambda m: f"(at {float(m.group(1)) + dx:.4f} {float(m.group(2)) + dy:.4f} {m.group(3)})",
        block,
    )
    block = re.sub(r'\(uuid "[^"]+"\)', lambda _: f'(uuid "{uuid_for(new_ref + ":uuid:" + str(uuid_for(new_ref + ":n")))}")', block, count=1)
    block = re.sub(r'\(uuid "[^"]+"\)', lambda m: f'(uuid "{uuid_for(new_ref + ":child:" + m.group(0))}")', block)
    block = block.replace(f'"{old_ref}"', f'"{new_ref}"')
    block = block.replace(f'(reference "{old_ref}")', f'(reference "{new_ref}")')
    return block


def wire(x: float, y1: float, y2: float, key: str) -> str:
    return (
        f'\t(wire\n'
        f'\t\t(pts (xy {x:.4f} {y1:.4f}) (xy {x:.4f} {y2:.4f}))\n'
        f'\t\t(stroke (width 0.254) (type default) (color 170 30 30 1))\n'
        f'\t\t(uuid "{uuid_for("wire:" + key)}")\n'
        f'\t)\n'
    )


def main() -> None:
    text = SCHEMATIC.read_text(encoding="utf-8")
    if 'property "Reference" "C6"' in text or 'property "Reference" "C7"' in text:
        if 'property "Reference" "C6"' in text and 'property "Reference" "C7"' in text:
            return
        raise RuntimeError("Schematic has only one of the expected C6/C7 symbols")
    base_cap = block_for_ref(text, "C4")
    templates = {
        "C6": [
            ("#PWR03", "#PWR60", 210.82, 91.44),
            ("#PWR25", "#PWR61", 210.82, 104.14),
        ],
        "C7": [
            ("#PWR13", "#PWR62", 137.16, 215.90),
            ("#PWR26", "#PWR63", 137.16, 228.60),
        ],
    }
    additions: list[str] = []
    for ref, (x, y) in PLACEMENTS.items():
        additions.append(clone_symbol(base_cap, "C4", ref, x - 210.82, y - 97.79))
        for old_power, new_power, base_x, base_y in templates[ref]:
            old_block = block_for_ref(text, old_power)
            vertical = -6.35 if old_power in {"#PWR03", "#PWR13"} else 6.35
            additions.append(clone_symbol(old_block, old_power, new_power, x - base_x, y + vertical - base_y))
        additions.append(wire(x, y - 3.81, y - 6.35, ref + ":top"))
        additions.append(wire(x, y + 3.81, y + 6.35, ref + ":bottom"))

    insertion = text.index("\n\t(sheet_instances\n")
    SCHEMATIC.write_text(text[:insertion] + "\n" + "\n".join(additions) + text[insertion:], encoding="utf-8", newline="\n")
    print("Added C6/C7 schematic symbols with 3V3/5V_SENSOR and GND power connections.")


if __name__ == "__main__":
    main()
