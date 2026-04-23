# toll-for-gps-tracks-csv-upload

Sample code showing how to use the TollGuru **GPS Tracks Toll API** to calculate tolls from GPS trace CSV files. Upload a CSV of GPS coordinates and receive toll costs for the matched route.

## What This Repo Is

A single-language (Python) reference implementation demonstrating the TollGuru GPS-tracks-csv-upload and csv-download endpoints. Includes sample CSV files for multiple countries.

## Architecture

- Standalone Python script, no framework or server
- Calls TollGuru REST API v2 (`/gps-tracks-csv-upload`, `/gps-tracks-csv-download`)
- Supports synchronous (immediate) and asynchronous (polled) upload modes
- Async mode: upload returns a `requestId`, then poll the download endpoint with retries
- Vehicle parameters (type, weight, height) are configurable in-script
- API key read from `TOLLGURU_API_KEY` environment variable
- Sample GPS CSV files provided in `Sample-GPS-tracks/` for 9 countries
- No database, no queue, no background jobs
- CI: GitHub Actions for Gitleaks (secret scanning) and Semgrep (SAST)
- Dependabot configured for dependency updates

## Prerequisites

- Python 3.7+
- `pip` for dependency management
- A valid [TollGuru API key](https://tollguru.com/blog/get-api-key)

## Local Setup

```bash
git clone <repo-url>
cd toll-for-gps-tracks-csv-upload
pip install requests
export TOLLGURU_API_KEY="your-key-here"
```

## How to Run

```bash
python gps-tracks-csv-upload.py
```

The script uploads `Sample-GPS-tracks/france-GPS-Track-sample.csv` by default. Edit the `payload` path in `gps_tracks_csv_upload()` to use a different file.

## How to Run Tests

No automated tests exist in this repo. Manual verification: run the script and inspect the JSON response for expected toll fields.

## How to Deploy

This is a client-side script, not a deployed service. Integrate the functions (`gps_tracks_csv_upload`, `gps_tracks_csv_download`) into your own application.

## Where Config Lives

| Setting        | Location                                         |
| -------------- | ------------------------------------------------ |
| API key        | `TOLLGURU_API_KEY` env var                       |
| API base URL   | `TOLLGURU_API_URL` in `gps-tracks-csv-upload.py` |
| Vehicle params | `PARAMETERS` dict in `gps-tracks-csv-upload.py`  |
| Sample data    | `Sample-GPS-tracks/` directory                   |

## Known Limitations

- Single language (Python only); no JS/Go/Ruby/PHP variants
- No automated tests or CI test step
- Hardcoded sample file path (`france-GPS-Track-sample.csv`) in upload function
- Async download uses fixed retry count (5) and delay (5s), not configurable via CLI/env
- No CLI argument parsing; all config is in-source
- No error handling for missing API key or network failures
- GPS CSV format requirements are not documented in this repo; see [TollGuru docs](https://tollguru.com/toll-api-docs)

## Further Reading

- [TollGuru API Docs](https://tollguru.com/toll-api-docs)
- [Vehicle type coverage](https://github.com/mapup/tollguru_vehicle_coverage/wiki/Vehicle-types-supported-by-TollGuru)
- [API parameter examples](https://github.com/mapup/tollguru-api-parameter-examples/tree/main/request-bodies/03-TollTally-GPS-Tracks-To-Toll)
