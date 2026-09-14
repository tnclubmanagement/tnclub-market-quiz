#!/usr/bin/env python3
"""Small JSON API and browser preview server for the marketplace catalog."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse
import hashlib
import json
import mimetypes
import os

ROOT = Path(__file__).resolve().parent
PACKS_PATH = ROOT / "data" / "packs"
WEB_ROOT = ROOT / "web"
HOST = os.environ.get("MARKET_HOST", "127.0.0.1")
PORT = int(os.environ.get("MARKET_PORT", "8080"))
MAX_PACK_BYTES = int(os.environ.get("MARKET_MAX_PACK_BYTES", str(10 * 1024 * 1024)))


def pack_body(payload):
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def load_catalog():
    packs = []
    for pack_path in sorted(PACKS_PATH.glob("*.json")):
        with pack_path.open(encoding="utf-8") as pack_file:
            pack = json.load(pack_file)
        body = pack_path.read_bytes()
        if len(body) > MAX_PACK_BYTES:
            raise ValueError(
                f"Pack {pack_path.name} exceeds the {MAX_PACK_BYTES}-byte limit"
            )
        pack.setdefault("is_free", True)
        pack["size_bytes"] = len(body)
        pack["sha256"] = hashlib.sha256(body).hexdigest()
        packs.append(pack)
    return {"schema_version": "1", "packs": packs}


def load_static_catalog():
    catalog = load_catalog()
    packs = []
    for pack in catalog["packs"]:
        metadata = {key: value for key, value in pack.items() if key != "quizzes"}
        metadata["pack_url"] = f"./packs/{pack['pack_id']}.json"
        packs.append(metadata)
    return {"schema_version": catalog["schema_version"], "packs": packs}


def filter_catalog(catalog, query):
    search = query.get("q", [""])[0].strip().lower()
    filters = {
        key: query.get(key, [""])[0].strip().lower()
        for key in ("subject", "level", "kind", "status")
    }
    packs = [
        pack for pack in catalog["packs"]
        if (not search or search in f'{pack.get("title", "")} {pack.get("description", "")}'.lower())
        and all(not value or str(pack.get(key, "")).lower() == value for key, value in filters.items())
    ]
    return {"schema_version": catalog["schema_version"], "packs": packs, "total": len(packs)}


class MarketHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):  # noqa: N802
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):  # noqa: N802
        request = urlparse(self.path)
        path = unquote(request.path)
        query = parse_qs(request.query)

        if path == "/api/health":
            return self.send_json({"ok": True})
        if path in ("/api/packs", "/api/v1/packs"):
            catalog = load_catalog()
            return self.send_json(filter_catalog(catalog, query))
        if path.startswith("/api/packs/") or path.startswith("/api/v1/packs/"):
            is_download = path.endswith("/download")
            pack_id = path.split("/packs/", 1)[1].strip("/").removesuffix("/download")
            pack = next(
                (item for item in load_catalog().get("packs", []) if item.get("pack_id") == pack_id),
                None,
            )
            if pack is None:
                return self.send_json({"error": "Pack not found"}, status=404)
            if is_download:
                return self.send_download(pack)
            return self.send_json(pack)
        if path == "/catalog.json":
            return self.send_json(load_static_catalog())
        if path.startswith("/packs/"):
            pack_name = Path(path.removeprefix("/packs/")).name
            if not pack_name.endswith(".json"):
                return self.send_json({"error": "Pack not found"}, status=404)
            return self.send_file(PACKS_PATH / pack_name)
        if path in ("/", "/index.html"):
            return self.send_file(WEB_ROOT / "index.html")

        self.send_json({"error": "Not found"}, status=404)

    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def send_download(self, payload):
        body = (PACKS_PATH / f"{payload['pack_id']}.json").read_bytes()
        if len(body) > MAX_PACK_BYTES:
            return self.send_json(
                {"error": "Pack exceeds the maximum download size"},
                status=413,
            )
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Disposition", f'attachment; filename="{payload["pack_id"]}.json"')
        self.send_header("Content-Length", str(len(body)))
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, file_path):
        try:
            body = file_path.read_bytes()
        except FileNotFoundError:
            return self.send_json({"error": "Preview not found"}, status=404)
        if file_path.parent == PACKS_PATH and len(body) > MAX_PACK_BYTES:
            return self.send_json(
                {"error": "Pack exceeds the maximum download size"},
                status=413,
            )
        content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format_string, *args):
        print(f"{self.address_string()} - {format_string % args}")


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), MarketHandler)
    print(f"Marketplace preview: http://{HOST}:{PORT}")
    print(f"JSON API:            http://{HOST}:{PORT}/api/packs")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server")
    finally:
        server.server_close()
