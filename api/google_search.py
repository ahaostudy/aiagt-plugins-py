from flask import Blueprint

from common.types import Req, Resp
from dto.google_search import GoogleSearchReq, ReadLinkReq
from service.google_search import GoogleSearchService

api = Blueprint('google_search', __name__)
_svc = GoogleSearchService()


@api.route('/google_search', methods=['POST'])
@Req.parser(body_type=GoogleSearchReq)
def google_search(req: Req[GoogleSearchReq]):
    resp = _svc.google_search(req.body)
    return Resp.success(resp).build()


@api.route('/read_link_raw', methods=['POST'])
@Req.parser(body_type=ReadLinkReq)
def read_link_raw(req: Req[ReadLinkReq]):
    resp = _svc.read_link_raw(req.body.url)
    return Resp.success(resp).build()


@api.route('/read_link_text', methods=['POST'])
@Req.parser(body_type=ReadLinkReq)
def read_link_text(req: Req[ReadLinkReq]):
    resp = _svc.read_link_text(req.body.url)
    return Resp.success(resp).build()
