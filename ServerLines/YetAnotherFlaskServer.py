from flask import Flask, request , jsonify
import QuestionGenerator.PDFManip as manip
import ScrapeLord.wikiLeaked as wiki
import QuestionGenerator.Qgen as qgen
from DBops.crud import insert,insert_rev
from json import loads
import time
from YetAnotherException import ServerError

app = Flask(__name__)
PAGE_NUMBER = 'pageNumber'

pdf_stored = None
wiki_content = None

CUSTOM_CONTENT = 'content'
PDF_FILE = 'file'
SUCCESS = 'Success'
FAILURE = 'Failure'
TOPIC = 'topic'
QUESTIONS = 'questions'
USER_ID = 'user'
SCORE = 'score'
ANSWER_RATING = 'answerRating'
QUESTION_RATING = 'questionRating'

def resetContents():
    wiki_content = None


# @app.route('/getQuestionsForPdf', methods=['POST'])
# def getQuestionsForPdf():
#     pageNumber = int(request.form[PAGE_NUMBER].replace('\r\n',' ').replace('\n','')) - 1
#     print (pageNumber)
#     textContent = manip.getPageContent(pageNumber , None)
#     # print (textContent)
#     questionsArray = qgen.getQuestions(textContent)
#     resp = {}
#     print (questionsArray)
#     return jsonify(questionsArray)

# @app.route('/getContentForPdf', methods=['POST'])
# def getContentForPdf():
#     print ('Storing file')
#     request.files[PDF_FILE].save(manip.DEFAULT_FILE)
#     return jsonify({"status":"success"})

@app.route('/addTime', methods=['POST'])
def addTime():
    score = manip.removeSlashN(request.form[SCORE])
    answerRating = manip.removeSlashN(request.form[ANSWER_RATING])
    questionRating = manip.removeSlashN(request.form[QUESTION_RATING])
    uid = loads(manip.removeSlashN(request.form[USER_ID]))
    resp = insert_rev(uid,answerRating,questionRating,score)
    print (resp)
    return jsonify({"SUCCESS":True})


@app.route('/getContentForTopic', methods=['POST'])
def getContentForTopic():
    try:
        topic = manip.removeSlashN(request.form[TOPIC])
        print(topic)
        init_time = time.time()
        uid = loads(manip.removeSlashN(request.form[USER_ID]))
        resp = insert(uid, 'TOPI2QUIZ', "LENGTH" + "::" + str(len(topic)) + "::" + topic)
        print(resp)

        print ("INS_time :", time.time() - init_time)
        content_tree, wiki_content, topic = wiki.getTreeForGivenTopic(topic)
        print ("CON_time :".time.time() - init_time)

        response = {}
        response[CUSTOM_CONTENT] = content_tree
        response[TOPIC] = topic
        response[USER_ID] = uid

        # return jsonify(response)
        return jsonify(content_tree)
    except Exception as ex:
        raise ServerError(str(ex))

@app.route('/getQuestionsForText', methods=['POST'])
def getQuestionsForText():

    try:
        content = manip.removeSlashN(request.form[CUSTOM_CONTENT])
        uid = manip.removeSlashN(loads(request.form[USER_ID]))
        print(uid)

        resp = insert(uid, 'TEXT2QUIZ', "LENGTH" + "::" + str(len(content)) + "::" + content[:20])
        init_time = time.time()
        print (resp)
        print ("INS_time :", time.time() - init_time)

        questionArray = qgen.getQuestions(content)

        print ("QUE_time :", time.time() - init_time)

        uid = request.form[USER_ID]
        response = {}
        response[QUESTIONS] = questionArray
        response[USER_ID] = uid

        # return jsonify(response)
        return jsonify(questionArray)

    except Exception as ex:
        raise ServerError(str(ex))


@app.errorhandler(ServerError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


if __name__ == '__main__':
    app.run(debug=True,
            use_reloader=False,
            host='0.0.0.0'
            ) #run app in debug mode on port 5000
