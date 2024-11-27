from flask import Flask, Blueprint
from dotenv import load_dotenv

from api import google_search

load_dotenv()
app = Flask(__name__)


@app.route('/')
def home():
    return 'Aiagt plugin apis'


v1 = Blueprint('api_v1', __name__)
v1.register_blueprint(google_search.api, url_prefix='/google_search')

app.register_blueprint(v1, url_prefix='/api/v1')

if __name__ == '__main__':
    app.run(debug=True)
