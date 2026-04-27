import argparse
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path


API_URL = "https://cloud-api.yandex.net/v1/disk/public/resources"


def fetch_json(url):
    with urllib.request.urlopen(url, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def build_resource_url(public_url, path):
    query = urllib.parse.urlencode({"public_key": public_url, "path": path, "limit": 100})
    return f"{API_URL}?{query}"


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Download one file from a public Yandex Disk folder.")
    parser.add_argument("--public-url", required=True)
    parser.add_argument("--path", required=True, help="Folder path inside public disk, e.g. /en.")
    parser.add_argument("--index", type=int, default=0, help="File index inside the folder.")
    parser.add_argument("--output-dir", default="data/unbake-vocals")
    args = parser.parse_args()

    resource = fetch_json(build_resource_url(args.public_url, args.path))
    files = [item for item in resource.get("_embedded", {}).get("items", []) if item.get("type") == "file"]
    if not files:
        raise SystemExit(f"No files found at {args.path}")
    if args.index >= len(files):
        raise SystemExit(f"Index {args.index} is out of range; found {len(files)} files")

    item = files[args.index]
    output_dir = Path(args.output_dir) / args.path.strip("/")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / item["name"]

    print(f"downloading: {item['path']} ({item.get('size', 0)} bytes)")
    urllib.request.urlretrieve(item["file"], output_path)
    print(f"saved: {output_path}")


if __name__ == "__main__":
    main()
