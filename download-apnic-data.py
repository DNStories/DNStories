import requests
from ratelimit import limits, sleep_and_retry
import string
import datetime
import json
import tqdm
from local_utils import load_m49
import os

APNIC_URL = 'https://stats.labs.apnic.net/rvrs/'
APNIC_DATA_DIR = 'apnic_data'


@sleep_and_retry
@limits(calls=150, period=1050)   # 1 request every 5 seconds
def download_region(region: str, ts: datetime.datetime):
    url = f"{APNIC_URL}{region}"
    params = {'hc': region, 'hs': 0, 'hf': 1}
    headers = {'User-Agent': 'Python Requests via .IE for analysis purposes'}
    ts_str = ts.strftime("%Y%m%dT%H%M%S")

    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        if not os.path.exists(APNIC_DATA_DIR):
            os.makedirs(APNIC_DATA_DIR)
        # Save the data
        with open(f"{APNIC_DATA_DIR}/apnic-rvrs.{region}.{ts_str}.json", "w") as fp:
            json.dump(response.json(), fp)


if __name__ == '__main__':
    now = datetime.datetime.utcnow()

    m49 = load_m49()

    for region in tqdm.tqdm(m49['region_code']):
        download_region(region=region, ts=now)
