from Constants import *
from ResponsePojos.BaseResponse import BaseResponse

class ContentResponse(BaseResponse):

    def setContent(self , content):
        self.response[CUSTOM_CONTENT] = content
