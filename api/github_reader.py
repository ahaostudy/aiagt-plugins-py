from flask import Blueprint
import json

from common.types import Req, Resp
from dto.github_reader import ReadProjectStructureReq
from service.github_reader import GithubReaderService

api = Blueprint('github_reader', __name__)
_svc = GithubReaderService()


@api.route('/read_project_structure', methods=['POST'])
@Req.parser(body_type=ReadProjectStructureReq)
def read_project_structure(req: Req[ReadProjectStructureReq]):
    owner, repo, path = req.body.owner, req.body.repo, req.body.path.strip('/')
    result = _svc.get_tree(owner, repo, path) if req.body.recursion else _svc.get_files(owner, repo, path)
    return Resp.success(result, encode=True).build()
