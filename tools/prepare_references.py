import json
import subprocess
import sys


REFERENCES = [
    {
        "artist": "Cœur de pirate",
        "track": "Place de la République",
        "output": "data/references/fr/coeur_place_republique.txt",
    },
    {
        "artist": "Би-2",
        "track": "Полковнику никто не пишет",
        "output": "data/references/ru/bi2_polkovniku.txt",
    },
]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    for item in REFERENCES:
        command = [
            sys.executable,
            "tools/download_lrclib_reference.py",
            "--artist",
            item["artist"],
            "--track",
            item["track"],
            "--output",
            item["output"],
            "--index",
            "0",
        ]
        print(json.dumps({"running": item}, ensure_ascii=False))
        subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
