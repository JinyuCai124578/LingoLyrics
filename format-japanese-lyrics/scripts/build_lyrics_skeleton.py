#!/usr/bin/env python3
"""Build a Markdown skeleton from lyric+translation and lyric+romaji files."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional, Tuple


def read_lines(path: Path) -> List[str]:
    text = path.read_text(encoding="utf-8-sig")
    return [line.rstrip() for line in text.splitlines() if line.strip()]


def pair_lines(lines: List[str], start: int) -> List[Tuple[str, str]]:
    body = lines[start:]
    pairs: List[Tuple[str, str]] = []
    for index in range(0, len(body), 2):
        first = body[index]
        second = body[index + 1] if index + 1 < len(body) else ""
        pairs.append((first, second))
    return pairs


def align_romaji(
    translation_pairs: List[Tuple[str, str]],
    romaji_lines: List[str],
    header_lines: int,
) -> Tuple[List[str], List[str]]:
    body = romaji_lines[header_lines:]
    romaji: List[str] = []
    warnings: List[str] = []
    cursor = 0

    for index, (japanese, _chinese) in enumerate(translation_pairs):
        next_japanese: Optional[str] = None
        if index + 1 < len(translation_pairs):
            next_japanese = translation_pairs[index + 1][0]

        if cursor >= len(body):
            warnings.append(f"line {index + 1}: missing romaji for {japanese!r}")
            romaji.append("")
            continue

        if body[cursor] != japanese:
            try:
                found_at = body.index(japanese, cursor + 1)
            except ValueError:
                warnings.append(
                    f"line {index + 1}: Japanese text not found in romaji file: {japanese!r}"
                )
                romaji.append("")
                continue

            skipped = body[cursor:found_at]
            warnings.append(
                f"line {index + 1}: skipped {len(skipped)} unmatched romaji-file line(s) before {japanese!r}"
            )
            cursor = found_at

        candidate_index = cursor + 1
        if candidate_index >= len(body) or body[candidate_index] == next_japanese:
            romaji.append(japanese)
            cursor += 1
        else:
            romaji.append(body[candidate_index])
            cursor += 2

    if cursor < len(body):
        warnings.append(f"unused trailing romaji-file lines: {len(body) - cursor}")

    return romaji, warnings


def build_markdown(
    translation_lines: List[str],
    romaji_lines: List[str],
    header_lines: int,
) -> Tuple[str, List[str]]:
    header = translation_lines[:header_lines]
    translation_pairs = pair_lines(translation_lines, header_lines)
    romaji_values, warnings = align_romaji(translation_pairs, romaji_lines, header_lines)

    blocks: List[str] = []
    blocks.extend(header)
    blocks.append("")
    blocks.append("---")

    for translation_pair, romaji in zip(translation_pairs, romaji_values):
        japanese_from_translation, chinese = translation_pair

        blocks.extend(
            [
                "",
                japanese_from_translation,
                romaji,
                chinese,
                "<!-- annotations -->",
                "",
                "---",
            ]
        )

    return "\n".join(blocks).rstrip() + "\n", warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--translation", required=True, type=Path)
    parser.add_argument("--romaji", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--header-lines", type=int, default=4)
    args = parser.parse_args()

    translation_lines = read_lines(args.translation)
    romaji_lines = read_lines(args.romaji)
    markdown, warnings = build_markdown(translation_lines, romaji_lines, args.header_lines)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")

    for warning in warnings:
        print(f"WARNING: {warning}")
    print(f"Wrote {args.output}")
    return 0 if not warnings else 2


if __name__ == "__main__":
    raise SystemExit(main())
