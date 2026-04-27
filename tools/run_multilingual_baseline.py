import json
import subprocess
import sys
import time
from pathlib import Path


SAMPLES = [
    {
        "id": "es_bellakeo",
        "language": "es",
        "audio": "data/unbake-vocals/es/Peso Pluma & Anitta - BELLAKEO.m4a",
        "reference": "data/references/es/peso_pluma_bellakeo.txt",
    },
    {
        "id": "fr_place_republique",
        "language": "fr",
        "audio": "data/unbake-vocals/fr/Cœur de pirate - Place de la République.m4a",
        "reference": "data/references/fr/coeur_place_republique.txt",
    },
    {
        "id": "ru_polkovniku",
        "language": "ru",
        "audio": "data/unbake-vocals/ru/Би-2 - Полковнику никто не пишет.m4a",
        "reference": "data/references/ru/bi2_polkovniku.txt",
    },
]


def run_command(command):
    completed = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8")
    return completed.stdout


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    summary = []
    for sample in SAMPLES:
        output = f"outputs/{sample['id']}.small.cpu.json"
        print(json.dumps({"sample": sample["id"], "status": "transcribing"}, ensure_ascii=False))
        started = time.perf_counter()
        transcribe_output = run_command(
            [
                sys.executable,
                "tools/transcribe.py",
                sample["audio"],
                "--output",
                output,
                "--model-size",
                "small",
                "--device",
                "cpu",
                "--compute-type",
                "int8",
                "--language",
                sample["language"],
                "--beam-size",
                "1",
            ]
        )
        print(transcribe_output.strip())

        metrics_raw = run_command(
            [
                sys.executable,
                "tools/evaluate_text.py",
                "--reference",
                sample["reference"],
                "--hypothesis",
                output,
            ]
        )
        metrics = json.loads(metrics_raw)
        result = {
            "sample": sample["id"],
            "language": sample["language"],
            "elapsedSeconds": round(time.perf_counter() - started, 3),
            "cer": metrics["cer"],
            "wer": metrics["wer"],
            "output": output,
        }
        summary.append(result)
        print(json.dumps(result, ensure_ascii=False))

    summary_path = Path("outputs/multilingual_baseline.small.cpu.summary.json")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved: {summary_path}")


if __name__ == "__main__":
    main()
