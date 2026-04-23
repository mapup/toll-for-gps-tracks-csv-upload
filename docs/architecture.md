# Architecture

## Major Services

- **TollGuru GPS Tracks API v2** - the sole external service. Two endpoints used:
  - `POST /gps-tracks-csv-upload` - accepts a CSV body, returns toll data (sync) or a request ID (async)
  - `POST /gps-tracks-csv-download` - polls for async results using the request ID

## Datastore Choices

None. This is a stateless script with no persistence layer.

## Queues / Jobs

None. Async mode is handled by client-side polling with retries (`gps_tracks_csv_download`).

## Third-Party Dependencies

- `requests` (HTTP client) - only runtime dependency
- See `pip install requests`; no `requirements.txt` exists in this repo

## Auth Model

API key authentication via `x-api-key` HTTP header. Key is sourced from the `TOLLGURU_API_KEY` environment variable.

## Tenancy Model

Not applicable. Single-user script; no multi-tenancy.
