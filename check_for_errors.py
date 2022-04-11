import requests


def check_for_errors(response):
    response.raise_for_status()
    if response.history:
        raise requests.HTTPError()
