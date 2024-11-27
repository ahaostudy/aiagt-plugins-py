from flask import Flask
from dotenv import load_dotenv
from api import api

load_dotenv()
app = Flask(__name__)

app.register_blueprint(api, url_prefix='/api/v1')


@app.route('/')
def home():
    return 'Aiagt plugin apis'


if __name__ == '__main__':
    app.run(debug=True)
