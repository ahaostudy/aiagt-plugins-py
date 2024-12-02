import os.path
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import requests


class GithubReaderService:
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

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

    def get_files(self, owner: str, repo: str, path: str) -> list['FileNode']:
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

    def get_tree(self, owner: str, repo: str, path: str) -> list['FileNode']:
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
            child_size = child.get('size')

            if len(child_path) > len(path) and child_path.startswith(path):
                node = FileNode(child_path, child_type, child_size, None)
                nodes[child_path] = node
                nodes[os.path.dirname(child_path)].append_child(node)

        return nodes[path].children

    @staticmethod
    def get_file_content(owner: str, repo: str, file: str) -> str:
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file}"
        headers = {
            "Accept": "application/vnd.github.v3.raw"
        }

        resp = requests.get(url, headers=headers)
        resp.raise_for_status()

        return resp.text

    def search_file_by_code(self, owner: str, repo: str, query: str) -> list[str]:
        url = f'https://api.github.com/search/code?q={query}+repo:{owner}/{repo}+in:file'
        headers = {"Accept": "application/vnd.github.v3.raw", 'Authorization': f'token {self.GITHUB_TOKEN}'}

        resp = requests.get(url, headers=headers)

        files = set()
        for item in resp.json().get('items'):
            files.add(item.get('path'))

        return list(files)

    def search_file_by_name(self, owner: str, repo: str, name: str) -> tuple[list[str], list[str]]:
        tree = self.get_tree(owner, repo, '')

        files, dirs = list(), list()
        stack, name = tree[:], name.lower()

        while stack:
            node: FileNode = stack.pop()
            if node.children:
                stack.extend(node.children)

            if name not in node.path.lower():
                continue
            if node.type == FileNodeType.DIR:
                dirs.append(node.path)
            else:
                files.append(node.path)

        return files, dirs


@dataclass
class FileNode:
    path: str
    type: 'FileNodeType'
    size: Optional[int]
    children: Optional[list['FileNode']]

    def append_child(self, node: 'FileNode'):
        if self.children is None:
            self.children = []
        self.children.append(node)


class FileNodeType(Enum):
    FILE = "file"
    DIR = "dir"
