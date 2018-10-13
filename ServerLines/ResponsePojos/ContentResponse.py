from Constants import *
from ResponsePojos.BaseResponse import BaseResponse

class ContentResponse(BaseResponse):
    """
    Content response class is used whenever content is returned. Here content refers to the content coming in from wikipedia.
    """
    def setContent(self , content):
        self.response[CUSTOM_CONTENT] = content