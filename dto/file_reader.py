from dataclasses import dataclass


@dataclass
class ReadFileReq:
    url: str
    type: str
