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
    result = svc.get_tree(owner, repo, path) if req.body.recursion else svc.get_files(owner, repo, path)
    return Resp.success(result, encode=True).build()


@api.route('/read_files_content', methods=['POST'])
@Req.parser(body_type=ReadFilesContentReq)
def read_files_content(req: Req[ReadFilesContentReq]):
    owner, repo, files = req.body.owner, req.body.repo, req.body.files
    result = [{
        "file": file,
        "content": svc.get_file_content(owner, repo, file.strip('/'))
    } for file in files]
    return Resp.success(result).build()


@api.route('/search_file', methods=['POST'])
@Req.parser(body_type=SearchFileReq)
def search_file(req: Req[SearchFileReq]):
    owner, repo, query = req.body.owner, req.body.repo, req.body.query.strip('/')

    files, dirs = svc.search_file_by_name(owner, repo, query)
    files.extend(svc.search_file_by_code(owner, repo, query))

    result = [{'path': f, 'type': 'file'} for f in files]
    result.extend([{'path': d, 'type': 'dir'} for d in dirs])
    result.sort(key=lambda x: x['path'])

    return Resp.success(result).build()
