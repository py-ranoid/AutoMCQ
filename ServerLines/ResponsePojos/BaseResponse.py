from Constants import *

class BaseResponse:
    """
    Base response class that is returned with every request sent to server.
    """
    def __init__(self):
        self.response = dict()
        self.response[RESPONSE_CODE] = SUCCESS_RESPONSE
        self.response[MESSAGE] = DEFAULT_MESSAGE

    def setUserInformation(self , uid):
        self.response[USER_ID] = uid

    def setResponseCode(self, response_code):
        self.response[RESPONSE_CODE] = response_code

    def setMessage(self, message):
        self.response[MESSAGE] = message

    def getResponse(self):
        return self.response