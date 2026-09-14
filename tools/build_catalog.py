#!/usr/bin/env python3
"""Build the static catalog consumed by the GitHub Pages frontend."""

from pathlib import Path
import hashlib
import json
import shutil


ROOT = Path(__file__).resolve().parents[1]
PACKS_PATH = ROOT / "data" / "packs"
OUTPUT_PATH = ROOT / "web" / "catalog.json"
PUBLIC_PACKS_PATH = ROOT / "web" / "packs"
MAX_PACK_BYTES = 10 * 1024 * 1024


def pack_body(payload):
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def build_catalog():
    packs = []
    PUBLIC_PACKS_PATH.mkdir(parents=True, exist_ok=True)
    for pack_path in sorted(PACKS_PATH.glob("*.json")):
        with pack_path.open(encoding="utf-8") as pack_file:
            pack = json.load(pack_file)
        body = pack_path.read_bytes()
        if len(body) > MAX_PACK_BYTES:
            raise ValueError(
                f"Pack {pack_path.name} exceeds the {MAX_PACK_BYTES}-byte limit"
            )
        metadata = {
            key: value for key, value in pack.items() if key != "quizzes"
        }
        metadata.setdefault("is_free", True)
        metadata["size_bytes"] = len(body)
        metadata["sha256"] = hashlib.sha256(body).hexdigest()
        metadata["pack_url"] = f"./packs/{pack_path.name}"
        shutil.copyfile(pack_path, PUBLIC_PACKS_PATH / pack_path.name)
        packs.append(metadata)
    return {"schema_version": "1", "packs": packs}


if __name__ == "__main__":
    catalog = build_catalog()
    OUTPUT_PATH.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(catalog['packs'])} packs to {OUTPUT_PATH}")
