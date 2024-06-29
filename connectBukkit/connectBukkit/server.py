import flask
from flask import request, abort

from 扩展组件.connectBukkit import config


class server:
    def __init__(self):
        self.app = flask.Flask(__name__)

        @self.app.before_request
        def inbound():
            if len(config.allow_IP) > 0:
                if request.remote_addr in config.allow_IP == False:
                    abort(403)

        @self.app.post("/sendMess")
        def sendMess():
            return ""

        @self.app.get("/getMess")
        def getMess():
            return ""
