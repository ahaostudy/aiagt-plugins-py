from dataclasses import dataclass
from typing import List


@dataclass
class GoogleSearchReq:
    query: str
    num: int = 3
    start: int = 0


@dataclass
class GoogleSearchItem:
    title: str
    link: str
    snippet: str


@dataclass
class GoogleSearchResp:
    items: List[GoogleSearchItem]


@dataclass
class ReadLinkReq:
    url: str
