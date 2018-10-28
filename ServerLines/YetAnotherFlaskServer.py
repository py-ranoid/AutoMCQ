from flask import Flask, request , jsonify
import QuestionGenerator.PDFManip as manip
from werkzeug.contrib.cache import MemcachedCache
import ScrapeLord.wikiLeaked as wiki
import QuestionGenerator.Qgen as qgen
from DBops.crud import insert,insert_rev
from json import loads
import sys, traceback
import time
from YetAnotherException import ServerError
from ResponsePojos.ContentResponse import ContentResponse
from ResponsePojos.QuestionResponse import QuestionReponse
from ResponsePojos.TopicsResponse import TopicsResponse
from Constants import *
from YesWeKhan.contentFetcher import get_transcript_from_URL
from ast import literal_eval
app = Flask(__name__)
cache = MemcachedCache(['127.0.0.1:11211'])

def get_my_item():
    rv = cache.get('my-item')
    if rv is None:
        rv = calculate_value()
        cache.set('my-item', rv, timeout=5 * 60)
    return rv
    
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
    """
    Given a topic name, the content for that topic is returned to be displayed to the user from wikipedia.
    :returns Returns a POJO in correspondence to ContentResponse()
    """
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
        mem_val = cache.get('CT-'+topic)
        if mem_val is None:
            print ("MEM IS NONE")
            content_tree = wiki.getTreeForFirstGivenTopic(topic)[0]
            cache.set('CT-'+topic, content_tree, timeout=500 * 60)
        else:
            content_tree = mem_val
        print ("CON_time :",time.time() - init_time)

        response = ContentResponse()
        response.setResponseCode(SUCCESS_RESPONSE)
        response.setContent(content_tree)
        return jsonify(response.getResponse())

    except ServerError as ex:
        traceback.print_exc()
        raise ex

    except Exception as ex:
        traceback.print_exc()
        raise ServerError('New Error: ' + str(ex))

@app.route('/getQuizfromKA', methods=['POST'])
def getQuestionsForKAurl():
    """
    Khan Academy Questions Generator.
    :return:
    """
    try:

        url = manip.removeSlashN(request.form['url'])

        print("getQuizfromKA Called: " + url)

        content = get_transcript_from_URL(url)

        user_info = request.form.get(USER_ID,DEFAULT_USER)

        resp = insertLog(QUIZ_FOR_KHAN, user_info, content)
        init_time = time.time()

        questionArray = qgen.getQuestions(content)

        outLog(init_time, resp)

        response = QuestionReponse()
        response.setQuestions(questionArray)

        return jsonify(response.getResponse())

    except ServerError as ex:
        traceback.print_exc()
        raise ex

    except Exception as ex:
        traceback.print_exc()
        raise ServerError('New Error: ' + str(ex))

def insertLog(quiz_info, user_info , allContent = ''):
    uid = loads(manip.removeSlashN(user_info))
    print('User id:', uid)
    contentInfo = str(len(allContent)) + "::" + allContent[:20]
    resp = insert(uid, quiz_info, "LENGTH" + "::" + contentInfo)
    return resp

def outLog(init_time , resp):
    print (resp)
    print ("Question Generation Time :", time.time() - init_time)

@app.route('/getQuestionsForWikiTopic', methods=['POST'])
def getQuestionsForWikiTopic():
    """
    Generates questions for the given wiki tree content and the sub topic to quiz on.

    QUIZ_TOPIC
    CUSTOM_CONTENT
    USER_ID
    :return: Questions Response Object
    """
    try:
        init_time = time.time()
        quiztopic = manip.removeSlashN(request.form[QUIZ_TOPIC])
        topicContent = literal_eval(request.form[CUSTOM_CONTENT])

        print("getQuestionsForWikiTopic Called: " + quiztopic)

        user_info = request.form.get(USER_ID, DEFAULT_USER)
        allContent, quizContent = wiki.getQuizData(topicContent , quiztopic)
        print ("PRC_time :", time.time() - init_time)
        resp = insertLog(QUIZ_FOR_WIKI_TOPIC , user_info , quizContent)
        print ("INS_time :", time.time() - init_time)
        
        questionArray = qgen.getWikiQuestions(allContent , quizContent)
        print ("QUE_time :", time.time() - init_time)
        
        response = QuestionReponse()
        response.setQuestions(questionArray)
        print ("RET_time :", time.time() - init_time)
        return jsonify(response.getResponse())

    except ServerError as ex:
        traceback.print_exc()
        raise ex

    except Exception as ex:
        traceback.print_exc()
        raise ServerError('New Error: ' + str(ex))

@app.route('/getQuestionsForText', methods=['POST'])
def getQuestionsForText():
    """
    Get the questions for any given text in accordance to QuestionResponse().
    :return:
    """
    try:
        content = manip.removeSlashN(request.form[CUSTOM_CONTENT])
        user_info = request.form.get(USER_ID,DEFAULT_USER)

        print(content)

        print("getQuestionsForText Called: " + content[:10])
        print("Content : " + content)

        resp = insertLog(QUIZ_FOR_TEXT, user_info, content)
        init_time = time.time()

        questionArray = qgen.getQuestions(content)

        outLog(init_time , resp)

        response = QuestionReponse()
        response.setQuestions(questionArray)

        return jsonify(response.getResponse())

    except ServerError as ex:
        traceback.print_exc()
        raise ex

    except Exception as ex:
        traceback.print_exc()
        raise ServerError('New Error: ' + str(ex))


@app.route('/getListOfTopics', methods=['POST'])
def getListOfTopics():
    """
    Gets the list of topics taking the topic as input from the incoming request.
    :return: Returns a list of topics if there are 1 or more, else returns ServerError.
    """
    try:
        topic = manip.removeSlashN(request.form[TOPIC])
        print("getListOfTopics Called " + topic)
    
        mem_val = cache.get('TL-'+topic)
        if mem_val is None:
            topics = wiki.getListOfValidTopics(topic)
            cache.set('TL-'+topic, topics, timeout=500 * 60)

        response = TopicsResponse()
        response.setMultipleTopics(topics)

        return jsonify(response.getResponse())

    except ServerError as ex:
        traceback.print_exc()
        raise ex

    except Exception as ex:
        traceback.print_exc()
        raise ServerError('New Error: ' + str(ex))

@app.route('/getTrendingTopics', methods=['POST'])
def getTrendingTopics():
    """
    Gets the list of trending topics. Static as of now.
    """
    try:
        topics = [
            'Game of Thrones',
            'Chennai',
            'Endhiran',
            'Battle of Plassey'
        ]
        response = TopicsResponse()
        response.setMultipleTopics(topics)

        return jsonify(response.getResponse())

    except ServerError as ex:
        traceback.print_exc()
        raise ex

    except Exception as ex:
        traceback.print_exc()
        raise ServerError('New Error: ' + str(ex))


@app.errorhandler(ServerError)
def handleInvalidUsage(error):
    """
    Exception handler to handle invalid usages
    :param error:
    :return:
    """
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


if __name__ == '__main__':
    print('Starting Server')
    app.run(debug=True,
            use_reloader=False,
            host='0.0.0.0',
            ) #run app in debug mode on port 5000
