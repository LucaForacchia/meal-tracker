import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
import logging

from infrastructure.web_controller import api

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

api.init_app(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Authorization') # list of allowed headers
    return response

logging.getLogger().setLevel(logging.DEBUG)
app.run(debug=False, host="0.0.0.0", port=5001)
