from Constants import *
from ResponsePojos.BaseResponse import BaseResponse
from YetAnotherException import ServerError

class QuestionReponse(BaseResponse):
    """
    Question response is the pojo used to return questions and relavant information. It raises an error if there aren't
    any questions.
    """
    def setQuestions(self, questions):
        self.response[QUESTIONS] = questions
        self.response[NUM_QUESTIONS] = len(questions)
        if(len(questions) == 0):
            raise ServerError(NO_QUESTIONS)

