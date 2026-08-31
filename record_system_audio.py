import argparse
import sys
import time
import wave
from pathlib import Path
from typing import Any, List, Optional


def load_audio_modules():
    try:
        import numpy as np
        import soundcard as sc
    except ImportError as exc:
        missing = getattr(exc, "name", None) or "soundcard/numpy"
        print(f"Missing dependency: {missing}", file=sys.stderr)
        print("Install with: python -m pip install soundcard numpy", file=sys.stderr)
        sys.exit(1)

    return np, sc


def list_devices(sc: Any) -> None:
    speakers = sc.all_speakers()
    default = sc.default_speaker()

    if not speakers:
        print("No speaker/output devices were found.")
        return

    print("Speaker/output devices:")
    for index, speaker in enumerate(speakers):
        marker = " (default)" if speaker.name == default.name else ""
        print(f"  {index}: {speaker.name}{marker}")


def choose_speaker(sc: Any, index: Optional[int]):
    speakers = sc.all_speakers()
    if not speakers:
        raise RuntimeError("No speaker/output devices were found.")

    if index is None:
        return sc.default_speaker()

    if index < 0 or index >= len(speakers):
        raise RuntimeError(f"Device index {index} is out of range. Use --list to see devices.")

    return speakers[index]


def speaker_loopback_microphone(sc: Any, speaker: Any):
    try:
        return sc.get_microphone(id=speaker.name, include_loopback=True)
    except Exception as exc:
        raise RuntimeError(
            "Could not open a loopback recorder for this speaker. "
            "Try another --device from --list, or make sure the speaker is enabled."
        ) from exc


def float_audio_to_pcm16(np: Any, audio: Any) -> bytes:
    clipped = np.clip(audio, -1.0, 1.0)
    return (clipped * 32767.0).astype(np.int16).tobytes()


def write_wav(np: Any, path: Path, chunks: List[Any], samplerate: int) -> None:
    if not chunks:
        raise RuntimeError("No audio was recorded.")

    audio = np.concatenate(chunks, axis=0)
    if audio.ndim == 1:
        audio = audio.reshape(-1, 1)

    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(audio.shape[1])
        wav_file.setsampwidth(2)
        wav_file.setframerate(samplerate)
        wav_file.writeframes(float_audio_to_pcm16(np, audio))


def record_loopback(
    output: Path,
    seconds: Optional[float],
    device_index: Optional[int],
    samplerate: int,
    chunk_seconds: float,
) -> None:
    np, sc = load_audio_modules()
    speaker = choose_speaker(sc, device_index)
    microphone = speaker_loopback_microphone(sc, speaker)
    chunk_frames = max(1, int(samplerate * chunk_seconds))
    chunks: List[Any] = []

    print(f"Recording system playback from: {speaker.name}")
    print(f"Output: {output}")
    if seconds is None:
        print("Press Ctrl+C to stop.")
    else:
        print(f"Duration: {seconds:.1f} seconds")

    start = time.monotonic()
    try:
        with microphone.recorder(samplerate=samplerate) as recorder:
            while True:
                elapsed = time.monotonic() - start
                if seconds is not None and elapsed >= seconds:
                    break

                if seconds is None:
                    frames = chunk_frames
                else:
                    remaining_frames = int((seconds - elapsed) * samplerate)
                    frames = min(chunk_frames, max(1, remaining_frames))

                chunks.append(recorder.record(numframes=frames))
                recorded = time.monotonic() - start
                if seconds is None:
                    print(f"\rRecorded {recorded:6.1f}s", end="", flush=True)
                else:
                    print(f"\rRecorded {min(recorded, seconds):6.1f}s / {seconds:.1f}s", end="", flush=True)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        print()

    write_wav(np, output, chunks, samplerate)
    print(f"Saved: {output.resolve()}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Record Windows system playback audio with WASAPI loopback."
    )
    parser.add_argument("-o", "--output", default="system_audio.wav", help="Output wav path.")
    parser.add_argument(
        "-t",
        "--seconds",
        type=float,
        default=None,
        help="Recording duration in seconds. Omit to record until Ctrl+C.",
    )
    parser.add_argument(
        "-d",
        "--device",
        type=int,
        default=None,
        help="Speaker/output device index from --list. Defaults to the current default speaker.",
    )
    parser.add_argument("--list", action="store_true", help="List speaker/output devices and exit.")
    parser.add_argument("--samplerate", type=int, default=48000, help="Sample rate. Default: 48000.")
    parser.add_argument(
        "--chunk-seconds",
        type=float,
        default=0.25,
        help="Internal capture chunk size in seconds. Default: 0.25.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.list:
        _, sc = load_audio_modules()
        list_devices(sc)
        return 0

    try:
        record_loopback(
            output=Path(args.output),
            seconds=args.seconds,
            device_index=args.device,
            samplerate=args.samplerate,
            chunk_seconds=args.chunk_seconds,
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
