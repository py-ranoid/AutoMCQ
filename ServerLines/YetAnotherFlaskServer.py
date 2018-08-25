from flask import Flask, request , jsonify
import QuestionGenerator.PDFManip as manip
import ScrapeLord.wikiLeaked as wiki
import QuestionGenerator.Qgen as qgen
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
USER_ID = 'uid'
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

@app.route('/getContentForTopic', methods=['POST'])
def getContentForTopic():
    try:
        topic = request.form[TOPIC].replace('\r\n',' ').replace('\n','')
        print(topic)
        content_tree, wiki_content, topic = wiki.getTreeForGivenTopic(topic)
        uid = request.form[USER_ID]

        response = {}
        response[CUSTOM_CONTENT] = content_tree
        response[TOPIC] = topic
        response[USER_ID] = uid

        #train word to vec here
        return jsonify(response)
    except Exception as ex:
        raise ServerError(str(ex))


@app.route('/getQuestionsForText', methods=['POST'])
def getQuestionsForText():
    try:
        content = request.form[CUSTOM_CONTENT].replace('\r\n',' ').replace('\n','')
        questionArray = qgen.getQuestions(content)
        uid = request.form[USER_ID]
        response = {}
        response[QUESTIONS] = questionArray
        response[USER_ID] = uid
        return jsonify(response)
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
