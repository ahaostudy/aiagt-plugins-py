from flask import Blueprint

import google_search

api = Blueprint('api_v1', __name__)
api.register_blueprint(google_search.api, url_prefix='/google_search')
