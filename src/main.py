import os
import logging

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime

from infrastructure.web_controller import api
from infrastructure.web_controller.configuration import load_config

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

api.init_app(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Authorization') # list of allowed headers
    return response
    
# Set logging
path_logs = os.path.join("logs", datetime.now().replace(microsecond=0).isoformat()+".log")
logging.basicConfig(filename=path_logs, 
    encoding='utf-8', 
    level=logging.DEBUG,
    format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S'
    )
logging.info("Welcome to backend logs :)\nServer configuration: %s" % str(load_config()))
app.run(debug=False, host="0.0.0.0", port=5001)
