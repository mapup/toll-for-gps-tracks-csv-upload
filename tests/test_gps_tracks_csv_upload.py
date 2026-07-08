"""Unit tests for the GPS tracks CSV upload/download script.

The script under test lives at the repo root as ``gps-tracks-csv-upload.py``.
Because the filename contains hyphens it cannot be imported with a normal
``import`` statement, so we load it via ``importlib``. All network access is
mocked — these tests never hit the real TollGuru API.
"""

import importlib.util
import json
import os
from pathlib import Path
from unittest import mock

import pytest

MODULE_PATH = Path(__file__).resolve().parent.parent / "gps-tracks-csv-upload.py"


def _load_module():
    # Ensure the module-level API key constant is a string, not None.
    os.environ.setdefault("TOLLGURU_API_KEY", "test-key")
    spec = importlib.util.spec_from_file_location("gps_tracks_csv_upload", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Loaded once; the ``if __name__ == "__main__"`` guard keeps import side-effect free.
gps = _load_module()


def test_upload_posts_csv_and_returns_response():
    fake_response = mock.Mock()
    with mock.patch.object(gps.requests, "request", return_value=fake_response) as req:
        result = gps.gps_tracks_csv_upload()

    assert result is fake_response
    method, url = req.call_args[0][0], req.call_args[0][1]
    kwargs = req.call_args[1]
    assert method == "POST"
    assert gps.GPS_UPLOAD_ENDPOINT in url
    assert "isAsync=False" in url
    assert kwargs["headers"]["Content-Type"] == "text/csv"


def test_upload_sets_async_flag_in_url():
    with mock.patch.object(gps.requests, "request", return_value=mock.Mock()) as req:
        gps.gps_tracks_csv_upload(is_async=True)

    url = req.call_args[0][1]
    assert "isAsync=True" in url


def test_download_returns_immediately_when_completed():
    resp = mock.Mock()
    resp.text = json.dumps({"status": "COMPLETED", "route": {}})
    with mock.patch.object(gps.requests, "request", return_value=resp) as req, \
            mock.patch.object(gps, "sleep"):
        result = gps.gps_tracks_csv_download("payload", retry=3, delay=0)

    assert result["status"] == "COMPLETED"
    assert req.call_count == 1


def test_download_retries_until_exhausted():
    resp = mock.Mock()
    resp.text = json.dumps({"status": "ERROR"})
    with mock.patch.object(gps.requests, "request", return_value=resp) as req, \
            mock.patch.object(gps, "sleep"):
        result = gps.gps_tracks_csv_download("payload", retry=2, delay=0)

    assert result["status"] == "ERROR"
    # retry=2 -> loop runs for count 2, 1, 0 => 3 attempts.
    assert req.call_count == 3


def test_download_stops_on_first_completed_status():
    err = mock.Mock()
    err.text = json.dumps({"status": "ERROR"})
    ok = mock.Mock()
    ok.text = json.dumps({"status": "COMPLETED"})
    with mock.patch.object(gps.requests, "request", side_effect=[err, ok, err]) as req, \
            mock.patch.object(gps, "sleep"):
        result = gps.gps_tracks_csv_download("payload", retry=5, delay=0)

    assert result["status"] == "COMPLETED"
    assert req.call_count == 2
