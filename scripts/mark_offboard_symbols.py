"""Apply native KiCad off-board flags to the protected-battery harness symbols."""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMATIC = ROOT / "hardware" / "SmartMark.kicad_sch"
OFF_BOARD = {"BT1": True, "J3": True, "J4": False}  # values mean included in BOM


def symbol_blocks(source: str):
    marker = "\n\t(symbol\n\t\t(lib_id "
    cursor = 0
    while (start := source.find(marker, cursor)) >= 0:
        open_at = start + 2
        depth = 0
        in_string = False
        escaped = False
        for index in range(open_at, len(source)):
            char = source[index]
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    yield start, index + 1, source[start:index + 1]
                    cursor = index + 1
                    break
        else:
            raise ValueError("Unbalanced symbol instance in schematic")


def transform(source: str, check_only: bool = False) -> str:
    changes = []
    seen = set()
    for start, end, block in symbol_blocks(source):
        ref = next((name for name in OFF_BOARD if f'(property "Reference" "{name}"' in block), None)
        if ref is None:
            continue
        seen.add(ref)
        target = '(on_board no)\n\t\t(property "exclude_from_board" "yes" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
        bom_value = "yes" if OFF_BOARD[ref] else "no"
        if f"(in_bom {bom_value})" in block and "(on_board no)" in block and '(property "exclude_from_board" "yes"' in block:
            continue
        if "(on_board yes)" not in block or "(in_bom yes)" not in block:
            raise ValueError(f"Unexpected existing flags on {ref}")
        updated = block.replace("(on_board yes)", target, 1)
        if ref == "J4":
            updated = updated.replace("(in_bom yes)", "(in_bom no)", 1)
        changes.append((start, end, updated))
    if seen != set(OFF_BOARD):
        raise ValueError(f"Expected off-board symbols {sorted(OFF_BOARD)}, found {sorted(seen)}")
    if check_only and changes:
        raise ValueError("Off-board flags need regeneration")
    for start, end, updated in reversed(changes):
        source = source[:start] + updated + source[end:]
    return source


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify that off-board flags are already set")
    args = parser.parse_args()
    original = SCHEMATIC.read_text(encoding="utf-8")
    updated = transform(original, check_only=args.check)
    if not args.check and updated != original:
        SCHEMATIC.write_text(updated, encoding="utf-8", newline="\n")
    print("Verified native KiCad off-board flags on BT1, J3, and J4." if args.check else "Marked BT1/J3/J4 off-board; excluded the contact-only J4 symbol from BOM.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
