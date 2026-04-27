import argparse
import json
import time
from pathlib import Path

from faster_whisper import WhisperModel


def format_lrc_timestamp(seconds):
    minutes = int(seconds // 60)
    remaining = seconds - minutes * 60
    return f"{minutes:02d}:{remaining:05.2f}"


def main():
    parser = argparse.ArgumentParser(description="Transcribe audio into LRCLIB-like timed lyrics JSON.")
    parser.add_argument("audio_path", help="Path to source audio file.")
    parser.add_argument("--output", required=True, help="Path to output JSON file.")
    parser.add_argument("--model-size", default="tiny", help="faster-whisper model size.")
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"], help="Inference device.")
    parser.add_argument("--compute-type", default="int8", help="CTranslate2 compute type.")
    parser.add_argument("--language", default=None, help="Optional language hint, e.g. en, ru, fr.")
    parser.add_argument("--beam-size", type=int, default=1, help="Beam size. 1 is fastest for baseline runs.")
    args = parser.parse_args()

    audio_path = Path(args.audio_path)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    model = WhisperModel(args.model_size, device=args.device, compute_type=args.compute_type)
    model_loaded_at = time.perf_counter()

    segments_iter, info = model.transcribe(
        str(audio_path),
        language=args.language,
        beam_size=args.beam_size,
        vad_filter=True,
        word_timestamps=True,
    )

    segments = []
    words = []

    for segment in segments_iter:
        text = segment.text.strip()
        if not text:
            continue

        segments.append(
            {
                "start": round(float(segment.start), 3),
                "end": round(float(segment.end), 3),
                "text": text,
            }
        )

        for word in segment.words or []:
            token = word.word.strip()
            if not token:
                continue
            words.append(
                {
                    "word": token,
                    "start": round(float(word.start), 3),
                    "end": round(float(word.end), 3),
                    "probability": round(float(word.probability), 4),
                }
            )

    finished = time.perf_counter()
    plain_lyrics = "\n".join(segment["text"] for segment in segments)
    synced_lyrics = "\n".join(
        f"[{format_lrc_timestamp(segment['start'])}] {segment['text']}" for segment in segments
    )

    result = {
        "sourceAudio": str(audio_path),
        "model": {
            "name": "faster-whisper",
            "size": args.model_size,
            "device": args.device,
            "computeType": args.compute_type,
            "beamSize": args.beam_size,
        },
        "detectedLanguage": getattr(info, "language", None),
        "languageProbability": round(float(getattr(info, "language_probability", 0.0)), 4),
        "duration": round(float(getattr(info, "duration", 0.0)), 3),
        "runtime": {
            "modelLoadSeconds": round(model_loaded_at - started, 3),
            "transcribeSeconds": round(finished - model_loaded_at, 3),
            "totalSeconds": round(finished - started, 3),
        },
        "plainLyrics": plain_lyrics,
        "syncedLyrics": synced_lyrics,
        "segments": segments,
        "words": words,
    }

    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result["runtime"], ensure_ascii=False))
    print(f"saved: {output_path}")


if __name__ == "__main__":
    main()
