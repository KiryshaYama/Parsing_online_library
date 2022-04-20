import requests


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError