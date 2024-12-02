from dataclasses import dataclass


@dataclass
class ReadProjectStructureReq:
    owner: str
    repo: str
    path: str
    recursion: bool


@dataclass
class ReadFilesContentReq:
    owner: str
    repo: str
    files: list[str]


@dataclass
class SearchFileReq:
    owner: str
    repo: str
    query: str
