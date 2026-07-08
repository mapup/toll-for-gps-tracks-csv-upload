import json
from time import sleep
import requests
import os

from urllib.parse import urlencode

TOLLGURU_API_KEY = os.environ.get("TOLLGURU_API_KEY")
TOLLGURU_API_URL = "https://apis.tollguru.com/toll/v2"

GPS_UPLOAD_ENDPOINT = "gps-tracks-csv-upload"
GPS_DOWNLOAD_ENDPOINT = "gps-tracks-csv-download"

# Configurable parameters for GPS upload endpoint
PARAMETERS = {
    "vehicle": {
        "weight": 3000,
        "height": 10,
        "type": "5AxlesTruck",
    },
}


# Upload CSV file - You can use the CSV format file as shown in the table below.
def gps_tracks_csv_upload(is_async: bool = False):
    payload = "Sample-GPS-tracks/france-GPS-Track-sample.csv"

    url = f"{TOLLGURU_API_URL}/{GPS_UPLOAD_ENDPOINT}?{urlencode({**PARAMETERS['vehicle'], 'isAsync': is_async})}"

    headers = {"x-api-key": TOLLGURU_API_KEY, "Content-Type": "text/csv"}

    with open(payload, "rb") as f:
        response = requests.request("POST", url, headers=headers, data=f)
        # response = json.loads(response.text)
    return response


# When isAsync is set to true, use this funcation to get the result by passing the return value from the gps_tracks_csv_upload
def gps_tracks_csv_download(
    response_from_gps_tracks_csv_upload, retry: int = 5, delay: int = 5
):
    count = retry  # number of retries before stoping
    status = "ERROR"
    response = None

    while count >= 0 and status == "ERROR":
        url = f"{TOLLGURU_API_URL}/{GPS_DOWNLOAD_ENDPOINT}"

        headers = {"x-api-key": TOLLGURU_API_KEY, "Content-Type": "application/json"}

        response = requests.request(
            "POST", url, headers=headers, data=response_from_gps_tracks_csv_upload
        )
        response = json.loads(response.text)
        status = response["status"]
        count -= 1
        sleep(delay)  # delay between each request.

    return response


if __name__ == "__main__":
    print(gps_tracks_csv_upload())
    print(
        gps_tracks_csv_download(
            response_from_gps_tracks_csv_upload=gps_tracks_csv_upload(is_async=True)
        )
    )
