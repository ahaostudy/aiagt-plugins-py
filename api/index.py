from flask import Flask, Blueprint, request
from dotenv import load_dotenv

from api import google_search, github_reader
from common.types import Resp

load_dotenv()
app = Flask(__name__)


@app.route('/')
def home():
    return 'Aiagt plugin apis'


@app.errorhandler(Exception)
def handle_exception(err: Exception):
    method = request.method
    url = request.url
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'unknown')

    error_msg = (
        f"[{method} {url}] "
        f"[Client-IP: {ip}] "
        f"[User-Agent: {user_agent}] "
        f"- {type(err).__name__}: {err}"
    )
    app.logger.error(error_msg)

    return Resp.internal_error(err).build()


v1 = Blueprint('api_v1', __name__)
v1.register_blueprint(google_search.api, url_prefix='/google_search')
v1.register_blueprint(github_reader.api, url_prefix='/github_reader')

app.register_blueprint(v1, url_prefix='/api/v1')

if __name__ == '__main__':
    app.run(debug=True)
