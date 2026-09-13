# TN Club Market

Minimal local web server for previewing the PRD-4 marketplace catalog.

## Run

```bash
python3 server.py
```

Open <http://127.0.0.1:8080> in a browser.

## JSON API

- `GET /api/health` — server health
- `GET /api/v1/packs` — complete catalog assembled from `data/packs/*.json`
- `GET /api/v1/packs/<pack_id>` — one pack
- `GET /api/packs` and `/api/packs/<pack_id>` — legacy preview aliases

Each pack has its own JSON file inside `data/packs/`. `data/market_catalog.json` is only the file index. Add or edit a pack file, refresh the browser, and the changes are immediately visible. The server uses only Python's standard library.
