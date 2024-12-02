from dataclasses import dataclass


@dataclass
class ReadProjectStructureReq:
    owner: str
    repo: str
    path: str
    recursion: bool
