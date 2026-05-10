import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional


LYRIC_URL = "https://music.163.com/api/song/media?id={song_id}"
AUDIO_URL = "http://music.163.com/song/media/outer/url?id={song_id}.mp3"


def extract_song_id(value: str) -> str:
    match = re.search(r"id=(\d+)", value)
    if match:
        return match.group(1)

    match = re.search(r"\b(\d{5,})\b", value)
    if match:
        return match.group(1)

    raise ValueError("No NetEase song id found.")


def read_id_file(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    return extract_song_id(text)


def request_url(url: str, timeout: int = 30) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            ),
            "Referer": "https://music.163.com/",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def download_lyric(song_id: str, output_path: Path, overwrite: bool) -> None:
    if output_path.exists() and not overwrite:
        print(f"Skip existing lyric: {output_path}")
        return

    raw = request_url(LYRIC_URL.format(song_id=song_id))
    try:
        data = json.loads(raw.decode("utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Lyric response is not JSON: {exc}") from exc

    if not isinstance(data, dict) or "lyric" not in data:
        raise RuntimeError("Lyric JSON does not contain a 'lyric' field.")

    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote lyric: {output_path}")


def download_audio(song_id: str, output_path: Path, overwrite: bool) -> None:
    if output_path.exists() and not overwrite:
        print(f"Skip existing audio: {output_path}")
        return

    raw = request_url(AUDIO_URL.format(song_id=song_id), timeout=60)
    if len(raw) < 1024:
        preview = raw[:200].decode("utf-8", errors="replace")
        raise RuntimeError(f"Audio response is unexpectedly small. Preview: {preview!r}")

    output_path.write_bytes(raw)
    print(f"Wrote audio: {output_path}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download NetEase lyric timeline JSON and audio by song id."
    )
    parser.add_argument(
        "song_id",
        nargs="?",
        help="NetEase song id, or a URL containing id=...",
    )
    parser.add_argument(
        "--id-file",
        type=Path,
        help="Read the song id from a text file such as 歌曲目录/id.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("."),
        help="Output folder. Defaults to current directory.",
    )
    parser.add_argument(
        "--lyric-name",
        default="时间轴.json",
        help="Output lyric timeline filename. Defaults to 时间轴.json.",
    )
    parser.add_argument(
        "--audio-name",
        default="音频.mp3",
        help="Output audio filename. Defaults to 音频.mp3.",
    )
    parser.add_argument(
        "--skip-audio",
        action="store_true",
        help="Only download the lyric timeline JSON.",
    )
    parser.add_argument(
        "--skip-lyric",
        action="store_true",
        help="Only download the audio file.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files.",
    )
    args = parser.parse_args()

    if args.id_file:
        song_id = read_id_file(args.id_file)
    elif args.song_id:
        song_id = extract_song_id(args.song_id)
    else:
        parser.error("Provide a song id, a URL containing id=..., or --id-file.")

    output_dir = args.out.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Song id: {song_id}")
    print(f"Output: {output_dir}")

    try:
        if not args.skip_lyric:
            download_lyric(song_id, output_dir / args.lyric_name, args.overwrite)
        if not args.skip_audio:
            download_audio(song_id, output_dir / args.audio_name, args.overwrite)
    except (urllib.error.URLError, urllib.error.HTTPError, RuntimeError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
