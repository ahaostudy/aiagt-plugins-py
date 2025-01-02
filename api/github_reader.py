from flask import Blueprint

from common.types import Req, Resp
from dto.github_reader import ReadProjectStructureReq, ReadFilesContentReq, SearchFileReq
from service.github_reader import GithubReaderService

api = Blueprint('github_reader', __name__)
svc = GithubReaderService()


@api.route('/read_project_structure', methods=['POST'])
@Req.parser(body_type=ReadProjectStructureReq)
def read_project_structure(req: Req[ReadProjectStructureReq]):
    owner, repo, path = req.body.owner, req.body.repo, req.body.path.strip('/')
    github_token = req.get_secret('GITHUB_TOKEN')
    result = svc.get_tree(owner, repo, path, github_token) \
        if req.body.recursion \
        else svc.get_files(owner, repo, path, github_token)
    return Resp.success(result, encode=True).build()


@api.route('/read_files_content', methods=['POST'])
@Req.parser(body_type=ReadFilesContentReq)
def read_files_content(req: Req[ReadFilesContentReq]):
    owner, repo, files = req.body.owner, req.body.repo, req.body.files
    github_token = req.get_secret('GITHUB_TOKEN')
    result = [{
        "file": file,
        "content": svc.get_file_content(owner, repo, file.strip('/'), github_token)
    } for file in files]
    return Resp.success(result).build()


@api.route('/search_file', methods=['POST'])
@Req.parser(body_type=SearchFileReq)
def search_file(req: Req[SearchFileReq]):
    owner, repo, query = req.body.owner, req.body.repo, req.body.query.strip('/')
    github_token = req.get_secret('GITHUB_TOKEN')

    files, dirs = svc.search_file_by_name(owner, repo, query, github_token)
    files.extend(svc.search_file_by_code(owner, repo, query, github_token))

    result = [{'path': f, 'type': 'file'} for f in files]
    result.extend([{'path': d, 'type': 'dir'} for d in dirs])
    result.sort(key=lambda x: x['path'])

    return Resp.success(result).build()
