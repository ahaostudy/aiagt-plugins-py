import os.path
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any
import requests


class GithubReaderService:
    @staticmethod
    def join_with_root(path1: str, path2: str) -> str:
        path = os.path.join(path1, path2)
        return path if path.startswith('/') else '/' + path

    @staticmethod
    def get_default_branch(owner: str, repo: str):
        """
        get the default branch of the repository
        """

        url = f'https://api.github.com/repos/{owner}/{repo}'
        resp = requests.get(url)

        resp.raise_for_status()
        return resp.json().get('default_branch')

    def get_files(self, owner: str, repo: str, path: str) -> List['FileNode']:
        """
        get all files under the specified path
        """

        url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
        resp = requests.get(url)
        resp.raise_for_status()

        children = list()
        for item in resp.json():
            child_path = self.join_with_root(path, item.get('name'))
            child_type = FileNodeType(item.get('type', 'file'))
            child_size = item.get('size')

            child = FileNode(child_path, child_type, child_size, None)
            children.append(child)
        return children

    def get_tree(self, owner: str, repo: str, path: str) -> List['FileNode']:
        """
        get the directory tree under the specified path
        """
        default_branch = self.get_default_branch(owner, repo)

        url = f'https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1'
        resp = requests.get(url)
        resp.raise_for_status()

        nodes = {path: FileNode(path, FileNodeType.DIR, 0, None)}

        for child in resp.json().get('tree'):
            child_path = child.get('path', '')
            child_type = FileNodeType.DIR if child.get('type') == 'tree' else FileNodeType.FILE

            if len(child_path) > len(path) and child_path.startswith(path):
                node = FileNode(child_path, child_type, child.get('size'), None)
                nodes[child_path] = node
                nodes[os.path.dirname(child_path)].append_child(node)

        return nodes[path].children


@dataclass
class FileNode:
    path: str
    type: 'FileNodeType'
    size: int
    children: Optional[List['FileNode']]

    def append_child(self, node: 'FileNode'):
        if self.children is None:
            self.children = []
        self.children.append(node)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'path': self.path,
            'type': self.type.value,
            'size': self.size,
            'children': [child.to_dict() for child in self.children] if self.children else None
        }


class FileNodeType(Enum):
    FILE = "file"
    DIR = "dir"
