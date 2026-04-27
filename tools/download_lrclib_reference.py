import argparse
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Download plain lyrics reference from LRCLIB search.")
    parser.add_argument("--artist", required=True)
    parser.add_argument("--track", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--index", type=int, default=0)
    args = parser.parse_args()

    query = urllib.parse.urlencode({"artist_name": args.artist, "track_name": args.track})
    url = f"https://lrclib.net/api/search?{query}"
    request = urllib.request.Request(url, headers={"User-Agent": "unbake-rd/0.1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        records = json.loads(response.read().decode("utf-8"))

    if not records:
        raise SystemExit("No LRCLIB records found")
    if args.index >= len(records):
        raise SystemExit(f"Index {args.index} is out of range; found {len(records)} records")

    record = records[args.index]
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(record.get("plainLyrics") or "", encoding="utf-8")
    print(
        json.dumps(
            {
                "id": record.get("id"),
                "trackName": record.get("trackName"),
                "artistName": record.get("artistName"),
                "duration": record.get("duration"),
                "output": str(output),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
