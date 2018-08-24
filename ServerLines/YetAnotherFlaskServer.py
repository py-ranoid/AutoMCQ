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
TOPIC = 'topic'
QUESTIONS = 'questions'
NO_QUESTIONS = 'No Questions Generated'
USER_ID = 'uid'

def resetContents():
    wiki_content = None


@app.route('/getQuestionsForPdf', methods=['POST'])
def getQuestionsForPdf():
    pageNumber = int(request.form[PAGE_NUMBER].replace('\r\n',' ').replace('\n','')) - 1
    print (pageNumber)
    textContent = manip.getPageContent(pageNumber, None)
    questionsArray = qgen.getQuestions(textContent)
    print (questionsArray)
    return jsonify(questionsArray)

@app.route('/getContentForPdf', methods=['POST'])
def getContentForPdf():
    try:
        print ('Storing file')
        request.files['file'].save(manip.DEFAULT_FILE)
        return jsonify(success=True)
    except Exception as ex:
        return ServerError(str(ex), status_code=400)

@app.route('/getContentForTopic', methods=['POST'])
def getContentForTopic():
    try:
        topic = request.form[TOPIC].replace('\r\n',' ').replace('\n','')
        userid = request.form[USER_ID]
        resetContents()
        content_tree, wiki_content, topic = wiki.getTreeForGivenTopic(topic)

        response = {}
        response[CUSTOM_CONTENT] = content_tree
        response[USER_ID] = userid
        response[TOPIC] = topic

        print(response)
        return jsonify(response)
    except Exception as ex:
        raise ServerError(str(ex), status_code=400)

@app.route('/getQuestionsForText', methods=['POST'])
def getQuestionsForText():
    try:
        content = request.form[CUSTOM_CONTENT].replace('\r\n',' ').replace('\n','')
        userid = request.form[USER_ID]
        questionArray = qgen.getQuestions(content)
        if(len(questionArray) > 0):
            response = {}
            response[QUESTIONS] = questionArray
            response[USER_ID] = userid
            print(response)
            return jsonify(response)
        else:
            raise ServerError(NO_QUESTIONS, status_code=200)
    except Exception as ex:
        raise ServerError(str(ex), status_code=400)


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
