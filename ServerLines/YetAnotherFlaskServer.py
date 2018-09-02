from flask import Flask, request , jsonify
import QuestionGenerator.PDFManip as manip
import ScrapeLord.wikiLeaked as wiki
import QuestionGenerator.Qgen as qgen
from DBops.crud import insert,insert_rev
from json import loads
import traceback
import time
from YetAnotherException import ServerError
from ResponsePojos.ContentResponse import ContentResponse
from ResponsePojos.QuestionResponse import QuestionReponse
from Constants import *
from YesWeKhan.contentFetcher import get_transcript_from_URL

app = Flask(__name__)


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

    user_info = request.form.get(USER_ID,DEFAULT_USER)
    print (user_info)
    uid = loads(manip.removeSlashN(user_info))

    resp = insert_rev(uid,answerRating,questionRating,score)
    print (resp)
    return jsonify({"SUCCESS":True})


@app.route('/getContentForTopic', methods=['POST'])
def getContentForTopic():
    try:
        topic = manip.removeSlashN(request.form[TOPIC])
        print(topic)
        init_time = time.time()

        user_info = request.form.get(USER_ID,DEFAULT_USER)
        print (user_info)
        uid = loads(manip.removeSlashN(user_info))

        resp = insert(uid, 'TOPI2QUIZ', "LENGTH" + "::" + str(len(topic)) + "::" + topic)
        print(resp)

        print ("INS_time :", time.time() - init_time)
        content_tree, wiki_content, topic = wiki.getTreeForGivenTopic(topic)
        print ("CON_time :",time.time() - init_time)

        response = ContentResponse()
        response.setResponseCode(SUCCESS_RESPONSE)
        response.setContent(content_tree)
        # return jsonify(response.getResponse())
        return jsonify(content_tree)

    except ServerError as ex:
        traceback.print_exc()
        raise ex

    except Exception as ex:
        traceback.print_exc()
        raise ServerError('New Error: ' + str(ex))

@app.route('/getQuizfromKA', methods=['POST'])
def getQuestionsForKAurl():
    try:
        url = manip.removeSlashN(request.form['url'])
        init_time = time.time()
        content = get_transcript_from_URL(url)
        print ("KHA_time :", time.time() - init_time)

        user_info = request.form.get(USER_ID,DEFAULT_USER)
        print (user_info)
        uid = loads(manip.removeSlashN(user_info))

        print('User id:' , uid)
        resp = insert(uid, 'KA2QUIZ', "LENGTH" + "::" + str(len(content)) + "::" + content[:20])
        print (resp)
        print ("INS_time :", time.time() - init_time)

        questionArray = qgen.getQuestions(content)

        print ("QUE_time :", time.time() - init_time)

        response = QuestionReponse()
        response.setQuestions(questionArray)

        # return jsonify(response.getResponse())
        return jsonify(questionArray)

    except ServerError as ex:
        traceback.print_exc()
        raise ex

    except Exception as ex:
        traceback.print_exc()
        raise ServerError('New Error: ' + str(ex))

@app.route('/getQuestionsForText', methods=['POST'])
def getQuestionsForText():

    try:
        content = manip.removeSlashN(request.form[CUSTOM_CONTENT])

        user_info = request.form.get(USER_ID,DEFAULT_USER)
        print (user_info)
        uid = loads(manip.removeSlashN(user_info))

        print('User id:' , uid)
        resp = insert(uid, 'TEXT2QUIZ', "LENGTH" + "::" + str(len(content)) + "::" + content[:20])
        init_time = time.time()
        print (resp)
        print ("INS_time :", time.time() - init_time)

        questionArray = qgen.getQuestions(content)

        print ("QUE_time :", time.time() - init_time)

        response = QuestionReponse()
        response.setQuestions(questionArray)

        # return jsonify(response.getResponse())
        return jsonify(questionArray)

    except ServerError as ex:
        traceback.print_exc()
        raise ex

    except Exception as ex:
        traceback.print_exc()
        raise ServerError('New Error: ' + str(ex))


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
