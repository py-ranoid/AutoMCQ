from Constants import *
from ResponsePojos.BaseResponse import BaseResponse
from YetAnotherException import ServerError

class QuestionReponse(BaseResponse):

    def setQuestions(self, questions):
        self.response[QUESTIONS] = questions
        if(len(questions) == 0):
            raise ServerError(NO_QUESTIONS)

