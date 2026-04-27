import argparse
import shutil
import json
import os
import sys
import time
from pathlib import Path

import imageio_ffmpeg
import whisperx


def configure_local_paths():
    project_root = Path(__file__).resolve().parents[1]
    cache_root = project_root / ".cache"

    defaults = {
        "HF_HOME": cache_root / "huggingface",
        "HUGGINGFACE_HUB_CACHE": cache_root / "huggingface" / "hub",
        "TORCH_HOME": cache_root / "torch",
        "TMP": cache_root / "tmp",
        "TEMP": cache_root / "tmp",
    }
    for key, value in defaults.items():
        os.environ.setdefault(key, str(value))
        Path(os.environ[key]).mkdir(parents=True, exist_ok=True)

    ffmpeg_path = Path(imageio_ffmpeg.get_ffmpeg_exe()).resolve()
    local_bin = cache_root / "bin"
    local_bin.mkdir(parents=True, exist_ok=True)
    local_ffmpeg = local_bin / "ffmpeg.exe"
    if not local_ffmpeg.exists():
        shutil.copy2(ffmpeg_path, local_ffmpeg)
    os.environ["PATH"] = f"{local_bin}{os.pathsep}{ffmpeg_path.parent}{os.pathsep}{os.environ.get('PATH', '')}"


def format_lrc_timestamp(seconds):
    minutes = int(seconds // 60)
    remaining = seconds - minutes * 60
    return f"{minutes:02d}:{remaining:05.2f}"


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    configure_local_paths()

    parser = argparse.ArgumentParser(description="Run WhisperX forced alignment over existing ASR segments.")
    parser.add_argument("--audio", required=True, help="Path to source audio file.")
    parser.add_argument("--transcript-json", required=True, help="Output JSON from tools/transcribe.py.")
    parser.add_argument("--output", required=True, help="Path to aligned JSON output.")
    parser.add_argument("--language", required=True, help="Language code, e.g. en, ru, fr.")
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    args = parser.parse_args()

    started = time.perf_counter()
    transcript = json.loads(Path(args.transcript_json).read_text(encoding="utf-8"))
    segments = [
        {"start": segment["start"], "end": segment["end"], "text": segment["text"]}
        for segment in transcript.get("segments", [])
        if segment.get("text")
    ]
    if not segments:
        raise SystemExit("No transcript segments to align")

    model_a, metadata = whisperx.load_align_model(language_code=args.language, device=args.device)
    model_loaded_at = time.perf_counter()
    aligned = whisperx.align(
        segments,
        model_a,
        metadata,
        args.audio,
        args.device,
        return_char_alignments=False,
        print_progress=False,
    )
    finished = time.perf_counter()

    aligned_segments = aligned.get("segments", [])
    aligned_words = aligned.get("word_segments", [])
    synced_lyrics = "\n".join(
        f"[{format_lrc_timestamp(segment['start'])}] {segment['text'].strip()}"
        for segment in aligned_segments
        if segment.get("text")
    )

    result = {
        **transcript,
        "alignment": {
            "name": "whisperx",
            "language": args.language,
            "device": args.device,
            "runtime": {
                "modelLoadSeconds": round(model_loaded_at - started, 3),
                "alignSeconds": round(finished - model_loaded_at, 3),
                "totalSeconds": round(finished - started, 3),
            },
        },
        "syncedLyrics": synced_lyrics,
        "segments": aligned_segments,
        "words": aligned_words,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(result["alignment"]["runtime"], ensure_ascii=False))
    print(f"saved: {output_path}")


if __name__ == "__main__":
    main()
