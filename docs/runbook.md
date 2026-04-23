# Runbook

## Common Failures and Recovery

| Failure | Cause | Fix |
|---|---|---|
| `KeyError` / `None` for API key | `TOLLGURU_API_KEY` not set | `export TOLLGURU_API_KEY="..."` before running |
| `FileNotFoundError` | Script run from wrong directory | `cd` into repo root so `Sample-GPS-tracks/` is reachable |
| `ConnectionError` / timeout | TollGuru API unreachable | Check network, retry, or verify API status at [status.tollguru.com](https://tollguru.com) |
| Async download returns `ERROR` after all retries | Processing not complete or invalid request | Increase `retry` / `delay` params in `gps_tracks_csv_download()` |
| `KeyError: 'routes'` | Malformed or empty CSV | Validate CSV has columns: `latitude`, `longitude`, (optional `timestamp`) |

## Rollback Basics

This is a standalone script with no deployment pipeline. Rollback = `git checkout` to a previous commit.

```bash
git log --oneline -5
git checkout <commit-hash> -- gps-tracks-csv-upload.py
```

## On-Call / Logs / Monitoring

- No deployed service, so no on-call or monitoring
- Script output goes to stdout; pipe to a file if needed: `python gps-tracks-csv-upload.py > output.log 2>&1`
- For production integration, wrap calls with your own logging/alerting

## Cron Jobs / Scheduled Jobs

None defined. If you schedule this script (e.g., via cron), ensure:
- `TOLLGURU_API_KEY` is available in the cron environment
- Working directory is set to the repo root

Example crontab entry:
```
0 */6 * * * cd /path/to/repo && TOLLGURU_API_KEY=xxx python gps-tracks-csv-upload.py >> /var/log/gps-tolls.log 2>&1
```

## Data Backfill Scripts

None. This repo does not persist data. For backfill of toll calculations, re-run the script with the desired CSV files.
