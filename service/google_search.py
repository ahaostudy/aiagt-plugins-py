import os

import requests
from bs4 import BeautifulSoup

from dto.google_search import GoogleSearchReq, GoogleSearchResp, GoogleSearchItem


class GoogleSearchService:
    GOOGLE_API_KEY = os.getenv("GOOGLE_SEARCH__GOOGLE_API_KEY")
    SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH__SEARCH_ENGINE_ID")
    HTTP_PROXY = os.getenv("GOOGLE_SEARCH__HTTP_PROXY")

    def get_http_client(self):
        if self.HTTP_PROXY:
            proxies = {
                "http": self.HTTP_PROXY,
                "https": self.HTTP_PROXY,
            }
            session = requests.Session()
            session.proxies.update(proxies)
            return session
        else:
            return requests.Session()

    def google_search(self, req: GoogleSearchReq) -> GoogleSearchResp:
        base_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.GOOGLE_API_KEY,
            "cx": self.SEARCH_ENGINE_ID,
            "q": req.query,
            "start": req.start + 1,
            "num": req.num
        }

        client = self.get_http_client()

        response = client.get(base_url, params=params)
        response.raise_for_status()

        search_resp = response.json()

        items = [
            GoogleSearchItem(
                title=item["title"],
                link=item["link"],
                snippet=item["snippet"]
            ) for item in search_resp.get("items", [])
        ]

        return GoogleSearchResp(items=items)

    @staticmethod
    def read_link_raw(url: str) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text

    def read_link_text(self, url: str) -> str:
        raw_html = self.read_link_raw(url)
        if raw_html.startswith("Error"):
            return raw_html
        soup = BeautifulSoup(raw_html, 'html.parser')
        return soup.get_text(strip=True)
