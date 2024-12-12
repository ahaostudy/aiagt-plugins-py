from flask import Blueprint

from common.types import Req, Resp
from dto.file_reader import ReadFileReq
from service.file_reader import FileReaderService

api = Blueprint('file_reader', __name__)
svc = FileReaderService()


@api.route('/read_file', methods=['POST'])
@Req.parser(body_type=ReadFileReq)
def read_project_structure(req: Req[ReadFileReq]):
    result = svc.read_file(req.body.url, req.body.type)
    return Resp.success(result, encode=True).build()
