from Constants import *
from ResponsePojos.BaseResponse import BaseResponse
from YetAnotherException import ServerError


class TopicsResponse(BaseResponse):
    """
    Content response class is used whenever content is returned. Here content refers to the content coming in from wikipedia.
    """

    def setMultipleTopics(self, topics):
        self.response[MULTIPLE_TOPICS] = len(topics)
        self.response[TOPIC] = topics[0]
        self.response[TOPIC_LIST] = topics

        if (len(topics) == 0):
            raise ServerError(NO_TOPICS)