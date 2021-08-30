from os import getenv

from loguru import logger
from requests import get
from requests.auth import HTTPBasicAuth

url = 'https://api.doppler.com/v3/configs/config/secrets'

query = {'project': 'discussion-fuel', 'config': 'prd'}

response = get(
    url,
    params=query,
    auth=HTTPBasicAuth(getenv('DF_DOPPLER_KEY'), ''),
)

response.raise_for_status()

config = {
    name: value['computed']
    for name, value in response.json()['secrets'].items()
}

logger.info('Retrived config from Doppler')


def get_config(name: str) -> str:
    return config[name]
