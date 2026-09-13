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

## GitHub Pages

The repository includes a GitHub Actions workflow at `.github/workflows/pages.yml`. It builds a metadata-only `web/catalog.json`, copies the full quiz packs to `web/packs/`, and deploys the `web/` directory to GitHub Pages. The catalog contains pack specifications and relative links; quiz questions remain in the individual pack files.

To build the static catalog locally:

```bash
python3 tools/build_catalog.py
```

In GitHub, open **Settings → Pages**, set **Source** to **GitHub Actions**, then push to `main`. The site URL will be shown in the workflow deployment summary and under the Pages settings.
