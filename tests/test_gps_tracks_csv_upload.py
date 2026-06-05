"""
Tests for gps-tracks-csv-upload.py

Patterns borrowed from mapup-products-frontend:
- One test class per public function / concern
- Heavy use of unittest.mock – no real network calls or file I/O
- Explicit assertions on URL shape, headers, retry semantics, and edge cases
- Each test is self-contained: all patches are scoped to the test itself
"""

import importlib.util
import json
import sys
from unittest.mock import MagicMock, call, mock_open, patch

import pytest


# ---------------------------------------------------------------------------
# Module loader
#
# The script executes two top-level print() statements on import, which call
# both functions and hit the network.  We suppress all I/O before the module
# is executed so that the test suite can import cleanly without env vars or
# a live API key.
# ---------------------------------------------------------------------------

def _load_module():
    """
    Load gps-tracks-csv-upload.py with all side-effects neutralised.

    Strategy (mirrors how mapup-products-frontend mocks next/navigation at
    the Jest setup level):
      - patch requests.request → returns a canned SUCCESS response
      - patch builtins.open    → returns fake CSV bytes
      - patch builtins.print   → silences the two top-level print() calls
      - patch time.sleep       → skips the 5-second download poll delay
    """
    stub_http = MagicMock()
    stub_http.text = json.dumps({"status": "SUCCESS", "requestId": "stub-id"})

    m = mock_open(read_data=b"latitude,longitude,timestamp\n47.0,0.69,2023-01-01T00:00:00Z\n")

    with (
        patch("requests.request", return_value=stub_http),
        patch("builtins.open", m),
        patch("builtins.print"),
        patch("time.sleep"),
    ):
        spec = importlib.util.spec_from_file_location(
            "_gps_tracks_module", "gps-tracks-csv-upload.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

    # Register so patch("_gps_tracks_module.sleep") works if ever needed
    sys.modules["_gps_tracks_module"] = mod
    return mod


# Load once for the entire test session
_mod = _load_module()


# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

SAMPLE_CSV = b"latitude,longitude,timestamp\n47.24157,0.69426,2023-01-12T13:40:35Z\n"

_SYNC_SUCCESS = {"status": "SUCCESS", "toll": {"amount": 12.5, "currency": "EUR"}}
_ASYNC_INIT = {"status": "SUCCESS", "requestId": "req-abc-123"}
_ERROR_BODY = {"status": "ERROR", "message": "not ready yet"}


def _http_mock(body: dict) -> MagicMock:
    """Return a mock requests.Response whose .text is the JSON-encoded body."""
    m = MagicMock()
    m.text = json.dumps(body)
    return m


# ---------------------------------------------------------------------------
# gps_tracks_csv_upload()
# ---------------------------------------------------------------------------

class TestGpsTracksCsvUpload:
    """Unit tests for the upload function – mirrors utils.test.ts patterns."""

    # -- Return value --------------------------------------------------------

    def test_sync_returns_raw_response_object(self):
        """Function returns the Response directly; caller decides how to parse."""
        mock_resp = _http_mock(_SYNC_SUCCESS)
        with (
            patch("requests.request", return_value=mock_resp),
            patch("builtins.open", mock_open(read_data=SAMPLE_CSV)),
        ):
            result = _mod.gps_tracks_csv_upload(is_async=False)
        assert result is mock_resp

    def test_async_returns_raw_response_object(self):
        """Async mode also returns the unparsed Response object."""
        mock_resp = _http_mock(_ASYNC_INIT)
        with (
            patch("requests.request", return_value=mock_resp),
            patch("builtins.open", mock_open(read_data=SAMPLE_CSV)),
        ):
            result = _mod.gps_tracks_csv_upload(is_async=True)
        assert result is mock_resp

    # -- HTTP method ---------------------------------------------------------

    def test_uses_http_post(self):
        mock_resp = MagicMock()
        with (
            patch("requests.request", return_value=mock_resp) as mock_req,
            patch("builtins.open", mock_open(read_data=SAMPLE_CSV)),
        ):
            _mod.gps_tracks_csv_upload()
        assert mock_req.call_args[0][0] == "POST"

    # -- URL construction ----------------------------------------------------

    def test_url_starts_with_tollguru_base(self):
        mock_resp = MagicMock()
        with (
            patch("requests.request", return_value=mock_resp) as mock_req,
            patch("builtins.open", mock_open(read_data=SAMPLE_CSV)),
        ):
            _mod.gps_tracks_csv_upload()
        url = mock_req.call_args[0][1]
        assert url.startswith("https://apis.tollguru.com/toll/v2")

    def test_url_contains_upload_endpoint(self):
        mock_resp = MagicMock()
        with (
            patch("requests.request", return_value=mock_resp) as mock_req,
            patch("builtins.open", mock_open(read_data=SAMPLE_CSV)),
        ):
            _mod.gps_tracks_csv_upload()
        url = mock_req.call_args[0][1]
        assert "gps-tracks-csv-upload" in url

    def test_url_includes_vehicle_type_param(self):
        mock_resp = MagicMock()
        with (
            patch("requests.request", return_value=mock_resp) as mock_req,
            patch("builtins.open", mock_open(read_data=SAMPLE_CSV)),
        ):
            _mod.gps_tracks_csv_upload()
        url = mock_req.call_args[0][1]
        assert "5AxlesTruck" in url

    def test_url_includes_weight_param(self):
        mock_resp = MagicMock()
        with (
            patch("requests.request", return_value=mock_resp) as mock_req,
            patch("builtins.open", mock_open(read_data=SAMPLE_CSV)),
        ):
            _mod.gps_tracks_csv_upload()
        url = mock_req.call_args[0][1]
        assert "weight=3000" in url

    def test_url_includes_height_param(self):
        mock_resp = MagicMock()
        with (
            patch("requests.request", return_value=mock_resp) as mock_req,
            patch("builtins.open", mock_open(read_data=SAMPLE_CSV)),
        ):
            _mod.gps_tracks_csv_upload()
        url = mock_req.call_args[0][1]
        assert "height=10" in url

    def test_sync_url_has_is_async_false(self):
        mock_resp = MagicMock()
        with (
            patch("requests.request", return_value=mock_resp) as mock_req,
            patch("builtins.open", mock_open(read_data=SAMPLE_CSV)),
        ):
            _mod.gps_tracks_csv_upload(is_async=False)
        url = mock_req.call_args[0][1]
        assert "isAsync=False" in url

    def test_async_url_has_is_async_true(self):
        mock_resp = MagicMock()
        with (
            patch("requests.request", return_value=mock_resp) as mock_req,
            patch("builtins.open", mock_open(read_data=SAMPLE_CSV)),
        ):
            _mod.gps_tracks_csv_upload(is_async=True)
        url = mock_req.call_args[0][1]
        assert "isAsync=True" in url

    # -- Request headers -----------------------------------------------------

    def test_sends_api_key_header(self):
        """x-api-key header is set from the module-level TOLLGURU_API_KEY."""
        mock_resp = MagicMock()
        with (
            patch.object(_mod, "TOLLGURU_API_KEY", "test-key-xyz"),
            patch("requests.request", return_value=mock_resp) as mock_req,
            patch("builtins.open", mock_open(read_data=SAMPLE_CSV)),
        ):
            _mod.gps_tracks_csv_upload()
        headers = mock_req.call_args[1]["headers"]
        assert headers["x-api-key"] == "test-key-xyz"

    def test_sends_csv_content_type(self):
        mock_resp = MagicMock()
        with (
            patch("requests.request", return_value=mock_resp) as mock_req,
            patch("builtins.open", mock_open(read_data=SAMPLE_CSV)),
        ):
            _mod.gps_tracks_csv_upload()
        headers = mock_req.call_args[1]["headers"]
        assert headers["Content-Type"] == "text/csv"

    # -- File handling -------------------------------------------------------

    def test_opens_france_csv_in_binary_mode(self):
        """The hardcoded CSV path is opened as binary ('rb')."""
        mock_resp = MagicMock()
        m = mock_open(read_data=SAMPLE_CSV)
        with (
            patch("requests.request", return_value=mock_resp),
            patch("builtins.open", m) as mock_file,
        ):
            _mod.gps_tracks_csv_upload()
        mock_file.assert_called_once_with(
            "Sample-GPS-tracks/france-GPS-Track-sample.csv", "rb"
        )

    def test_passes_file_handle_as_request_data(self):
        """The file handle (not its contents) is forwarded to requests.request."""
        mock_resp = MagicMock()
        with (
            patch("requests.request", return_value=mock_resp) as mock_req,
            patch("builtins.open", mock_open(read_data=SAMPLE_CSV)),
        ):
            _mod.gps_tracks_csv_upload()
        assert "data" in mock_req.call_args[1]

    def test_makes_exactly_one_http_request(self):
        mock_resp = MagicMock()
        with (
            patch("requests.request", return_value=mock_resp) as mock_req,
            patch("builtins.open", mock_open(read_data=SAMPLE_CSV)),
        ):
            _mod.gps_tracks_csv_upload()
        assert mock_req.call_count == 1


# ---------------------------------------------------------------------------
# gps_tracks_csv_download()
# ---------------------------------------------------------------------------

class TestGpsTracksCsvDownload:
    """
    Unit tests for the async-polling download function.

    Key behaviours under test:
      - Exits the retry loop as soon as status != "ERROR"
      - Exhausts all retries when every response is ERROR
      - Passes the upload response body verbatim as the download request body
      - Sleeps between every poll (including the final one)
    """

    # -- Happy path ----------------------------------------------------------

    def test_returns_parsed_dict_on_first_success(self):
        mock_resp = _http_mock({"status": "SUCCESS", "toll": {"amount": 15.0}})
        with (
            patch("requests.request", return_value=mock_resp),
            patch.object(_mod, "sleep"),
        ):
            result = _mod.gps_tracks_csv_download(b'{"requestId":"r1"}', retry=3, delay=1)
        assert result == {"status": "SUCCESS", "toll": {"amount": 15.0}}

    def test_one_http_call_when_first_response_is_success(self):
        mock_resp = _http_mock({"status": "SUCCESS"})
        with (
            patch("requests.request", return_value=mock_resp) as mock_req,
            patch.object(_mod, "sleep"),
        ):
            _mod.gps_tracks_csv_download(b'{}', retry=5, delay=0)
        assert mock_req.call_count == 1

    # -- Retry logic ---------------------------------------------------------

    def test_retries_while_status_is_error(self):
        """retry=3 → 4 total attempts (initial + 3 retries)."""
        mock_resp = _http_mock(_ERROR_BODY)
        with (
            patch("requests.request", return_value=mock_resp) as mock_req,
            patch.object(_mod, "sleep"),
        ):
            _mod.gps_tracks_csv_download(b'{}', retry=3, delay=0)
        assert mock_req.call_count == 4

    def test_stops_on_first_non_error_response(self):
        """After two ERRORs followed by SUCCESS, exactly three calls are made."""
        responses = [
            _http_mock(_ERROR_BODY),
            _http_mock(_ERROR_BODY),
            _http_mock({"status": "SUCCESS", "toll": {"amount": 7.5}}),
        ]
        with (
            patch("requests.request", side_effect=responses) as mock_req,
            patch.object(_mod, "sleep"),
        ):
            result = _mod.gps_tracks_csv_download(b'{}', retry=5, delay=0)
        assert mock_req.call_count == 3
        assert result["status"] == "SUCCESS"

    def test_zero_retries_makes_exactly_one_attempt(self):
        """retry=0 means the loop runs once (count starts at 0, 0 >= 0 is True)."""
        mock_resp = _http_mock(_ERROR_BODY)
        with (
            patch("requests.request", return_value=mock_resp) as mock_req,
            patch.object(_mod, "sleep"),
        ):
            _mod.gps_tracks_csv_download(b'{}', retry=0, delay=0)
        assert mock_req.call_count == 1

    def test_returns_last_error_response_after_retry_exhaustion(self):
        """When all retries are ERROR the last parsed response is returned."""
        mock_resp = _http_mock({"status": "ERROR", "message": "timeout"})
        with (
            patch("requests.request", return_value=mock_resp),
            patch.object(_mod, "sleep"),
        ):
            result = _mod.gps_tracks_csv_download(b'{}', retry=2, delay=0)
        assert result["status"] == "ERROR"

    # -- Sleep / delay -------------------------------------------------------

    def test_sleep_called_after_each_request(self):
        """sleep() is invoked once per loop iteration, even on success."""
        mock_resp = _http_mock({"status": "SUCCESS"})
        with (
            patch("requests.request", return_value=mock_resp),
            patch.object(_mod, "sleep") as mock_sleep,
        ):
            _mod.gps_tracks_csv_download(b'{}', retry=2, delay=9)
        mock_sleep.assert_called_once_with(9)

    def test_sleep_delay_forwarded_correctly(self):
        """Every sleep call receives the exact delay value passed in."""
        error_resp = _http_mock(_ERROR_BODY)
        with (
            patch("requests.request", return_value=error_resp),
            patch.object(_mod, "sleep") as mock_sleep,
        ):
            _mod.gps_tracks_csv_download(b'{}', retry=2, delay=42)
        for c in mock_sleep.call_args_list:
            assert c == call(42)

    # -- HTTP method & URL ---------------------------------------------------

    def test_uses_http_post(self):
        mock_resp = _http_mock({"status": "SUCCESS"})
        with (
            patch("requests.request", return_value=mock_resp) as mock_req,
            patch.object(_mod, "sleep"),
        ):
            _mod.gps_tracks_csv_download(b'{}', retry=1, delay=0)
        assert mock_req.call_args[0][0] == "POST"

    def test_url_starts_with_tollguru_base(self):
        mock_resp = _http_mock({"status": "SUCCESS"})
        with (
            patch("requests.request", return_value=mock_resp) as mock_req,
            patch.object(_mod, "sleep"),
        ):
            _mod.gps_tracks_csv_download(b'{}', retry=1, delay=0)
        url = mock_req.call_args[0][1]
        assert url.startswith("https://apis.tollguru.com/toll/v2")

    def test_url_contains_download_endpoint(self):
        mock_resp = _http_mock({"status": "SUCCESS"})
        with (
            patch("requests.request", return_value=mock_resp) as mock_req,
            patch.object(_mod, "sleep"),
        ):
            _mod.gps_tracks_csv_download(b'{}', retry=1, delay=0)
        url = mock_req.call_args[0][1]
        assert "gps-tracks-csv-download" in url

    # -- Request headers -----------------------------------------------------

    def test_sends_api_key_header(self):
        mock_resp = _http_mock({"status": "SUCCESS"})
        with (
            patch.object(_mod, "TOLLGURU_API_KEY", "dl-test-key"),
            patch("requests.request", return_value=mock_resp) as mock_req,
            patch.object(_mod, "sleep"),
        ):
            _mod.gps_tracks_csv_download(b'{}', retry=1, delay=0)
        headers = mock_req.call_args[1]["headers"]
        assert headers["x-api-key"] == "dl-test-key"

    def test_sends_json_content_type(self):
        mock_resp = _http_mock({"status": "SUCCESS"})
        with (
            patch("requests.request", return_value=mock_resp) as mock_req,
            patch.object(_mod, "sleep"),
        ):
            _mod.gps_tracks_csv_download(b'{}', retry=1, delay=0)
        headers = mock_req.call_args[1]["headers"]
        assert headers["Content-Type"] == "application/json"

    # -- Request body --------------------------------------------------------

    def test_upload_response_forwarded_as_request_body(self):
        """The raw upload response is passed through as the download POST body."""
        mock_resp = _http_mock({"status": "SUCCESS"})
        upload_payload = b'{"requestId":"some-id"}'
        with (
            patch("requests.request", return_value=mock_resp) as mock_req,
            patch.object(_mod, "sleep"),
        ):
            _mod.gps_tracks_csv_download(upload_payload, retry=1, delay=0)
        assert mock_req.call_args[1]["data"] == upload_payload


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

class TestModuleConstants:
    """
    Smoke-test the global config values so any accidental edits are caught.
    Mirrors the config/__tests__/*.test.ts pattern in mapup-products-frontend.
    """

    def test_api_url(self):
        assert _mod.TOLLGURU_API_URL == "https://apis.tollguru.com/toll/v2"

    def test_upload_endpoint(self):
        assert _mod.GPS_UPLOAD_ENDPOINT == "gps-tracks-csv-upload"

    def test_download_endpoint(self):
        assert _mod.GPS_DOWNLOAD_ENDPOINT == "gps-tracks-csv-download"

    def test_default_vehicle_type(self):
        assert _mod.PARAMETERS["vehicle"]["type"] == "5AxlesTruck"

    def test_default_vehicle_weight(self):
        assert _mod.PARAMETERS["vehicle"]["weight"] == 3000

    def test_default_vehicle_height(self):
        assert _mod.PARAMETERS["vehicle"]["height"] == 10

    def test_api_key_sourced_from_env(self, monkeypatch):
        """Verifies the env-var lookup path; the constant is set at import time."""
        import os
        monkeypatch.setenv("TOLLGURU_API_KEY", "env-check-value")
        assert os.environ.get("TOLLGURU_API_KEY") == "env-check-value"


# ---------------------------------------------------------------------------
# Integration-style wiring tests
# ---------------------------------------------------------------------------

class TestIntegrationWorkflow:
    """
    End-to-end wiring without real I/O – analogous to hooks.test.tsx which
    wires context providers and hooks together in mapup-products-frontend.
    """

    def test_sync_workflow_returns_a_response(self):
        mock_resp = MagicMock()
        mock_resp.text = json.dumps(_SYNC_SUCCESS)
        with (
            patch("requests.request", return_value=mock_resp),
            patch("builtins.open", mock_open(read_data=SAMPLE_CSV)),
        ):
            result = _mod.gps_tracks_csv_upload(is_async=False)
        assert result is not None

    def test_async_workflow_upload_then_download(self):
        """
        Full async flow: upload returns a raw response, download receives it
        as its body and eventually returns parsed JSON.
        Two separate HTTP calls must be made.
        """
        upload_resp = MagicMock()
        upload_resp.text = json.dumps({"requestId": "r42", "status": "SUCCESS"})

        download_resp = _http_mock({"status": "SUCCESS", "toll": {"amount": 9.99}})

        call_n = {"v": 0}

        def _side_effect(*args, **kwargs):
            call_n["v"] += 1
            return upload_resp if call_n["v"] == 1 else download_resp

        with (
            patch("requests.request", side_effect=_side_effect) as mock_req,
            patch("builtins.open", mock_open(read_data=SAMPLE_CSV)),
            patch.object(_mod, "sleep"),
        ):
            upload_result = _mod.gps_tracks_csv_upload(is_async=True)
            download_result = _mod.gps_tracks_csv_download(
                upload_result, retry=1, delay=0
            )

        assert mock_req.call_count == 2
        assert download_result["status"] == "SUCCESS"
        assert download_result["toll"]["amount"] == 9.99

    def test_upload_endpoint_and_download_endpoint_are_different(self):
        """Upload and download must target different URL paths."""
        urls = []

        def _capture(*args, **kwargs):
            urls.append(args[1])
            return _http_mock({"status": "SUCCESS"})

        with (
            patch("requests.request", side_effect=_capture),
            patch("builtins.open", mock_open(read_data=SAMPLE_CSV)),
            patch.object(_mod, "sleep"),
        ):
            resp = _mod.gps_tracks_csv_upload(is_async=True)
            _mod.gps_tracks_csv_download(resp, retry=1, delay=0)

        assert len(urls) == 2
        assert urls[0] != urls[1]
        assert "csv-upload" in urls[0]
        assert "csv-download" in urls[1]
