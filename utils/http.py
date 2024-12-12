import os

import requests

HTTP_PROXY = os.getenv("HTTP_PROXY")

def client():
    if HTTP_PROXY:
        proxies = {
            "http": HTTP_PROXY,
            "https": HTTP_PROXY,
        }
        session = requests.Session()
        session.proxies.update(proxies)
        return session
    else:
        return requests.Session()
