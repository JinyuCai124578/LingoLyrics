#!/usr/bin/env python3
"""Build a Markdown skeleton from a French lyric+translation file."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Tuple


def read_lines(path: Path) -> List[str]:
    text = path.read_text(encoding="utf-8-sig")
    return [line.rstrip() for line in text.splitlines() if line.strip()]


def pair_lines(lines: List[str], start: int) -> Tuple[List[Tuple[str, str]], List[str]]:
    body = lines[start:]
    warnings: List[str] = []
    pairs: List[Tuple[str, str]] = []

    if len(body) % 2 != 0:
        warnings.append(
            f"odd number of body lines after header: {len(body)}; last translation may be blank"
        )

    for index in range(0, len(body), 2):
        french = body[index]
        chinese = body[index + 1] if index + 1 < len(body) else ""
        pairs.append((french, chinese))

    return pairs, warnings


def build_markdown(input_lines: List[str], header_lines: int) -> Tuple[str, List[str]]:
    header = input_lines[:header_lines]
    pairs, warnings = pair_lines(input_lines, header_lines)

    blocks: List[str] = []
    blocks.extend(header)
    blocks.append("")
    blocks.append("---")

    for french, chinese in pairs:
        blocks.extend(
            [
                "",
                french,
                "<!-- phonetics -->",
                chinese,
                "<!-- annotations -->",
                "",
                "---",
            ]
        )

    return "\n".join(blocks).rstrip() + "\n", warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--header-lines", type=int, default=4)
    args = parser.parse_args()

    input_lines = read_lines(args.input)
    markdown, warnings = build_markdown(input_lines, args.header_lines)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")

    for warning in warnings:
        print(f"WARNING: {warning}")
    print(f"Wrote {args.output}")
    return 0 if not warnings else 2


if __name__ == "__main__":
    raise SystemExit(main())
