from Constants import *

class ServerError(Exception):
    status_code = 200

    def __init__(self, message, response_code=0, payload=None):
        Exception.__init__(self)
        self.message = message
        self.response_code = response_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv[MESSAGE] = self.message
        rv[RESPONSE_CODE] = 0
        return rv
