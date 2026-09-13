# TN Club Market Specification

## Purpose

`tnclub_market` is the catalog source for the Flutter Marketplace screen. It serves pack metadata only; quiz files, authentication, payments, and downloads are outside this service.

## Pack files

Each pack is one JSON file in `data/packs/`. The required fields are:

```json
{
  "pack_id": "react-fundamentals",
  "title": "React Fundamentals",
  "description": "...",
  "subject": "React",
  "level": "Beginner",
  "kind": "Standard",
  "content_version": "1",
  "question_count": 30,
  "status": "available"
}
```

Allowed `status` values are `available`, `installed`, `update_available`, and `unavailable`.

`data/market_catalog.json` is only an index of pack file paths. The server discovers `data/packs/*.json` when a request arrives, so adding a pack does not require code changes.

## API

Base URL for local development: `http://127.0.0.1:8080`

### Health

```http
GET /api/health
```

### Catalog

```http
GET /api/v1/packs
```

Optional case-insensitive query parameters:

- `q` — search title and description
- `subject`
- `level`
- `kind`
- `status`

Example:

```text
/api/v1/packs?q=redux&subject=React&level=Advanced
```

Response:

```json
{
  "schema_version": "1",
  "packs": [],
  "total": 0
}
```

### One pack

```http
GET /api/v1/packs/<pack_id>
```

### Download pack JSON

```http
GET /api/v1/packs/<pack_id>/download
```

The response is an attachment named `<pack_id>.json`. The current fixture files contain catalog metadata; full quiz content must be added to a pack before it can be installed and opened as a quiz.

The older `/api/packs` paths remain available for the preview UI.

## Flutter integration

The Flutter app should depend on the response fields above through a repository, not call HTTP from widgets. For Chrome development, start this server before opening `/market`:

```bash
python3 server.py
```

The server sends permissive CORS headers for local development. Production deployment must restrict allowed origins.
