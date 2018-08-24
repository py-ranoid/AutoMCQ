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

def resetContents():
    wiki_content = None


@app.route('/getQuestionsForPdf', methods=['POST'])
def getQuestionsForPdf():
    pageNumber = int(request.form[PAGE_NUMBER].replace('\r\n',' ').replace('\n','')) - 1
    print (pageNumber)
    textContent = manip.getPageContent(pageNumber , None)
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
        resetContents()
        content_tree , wiki_content = wiki.getTreeForGivenTopic(topic)
        return jsonify(content_tree)
    except Exception as ex:
        raise ServerError(str(ex), status_code=400)

@app.route('/getQuestionsForText', methods=['POST'])
def getQuestionsForText():
    try:
        content = request.form['content'].replace('\r\n',' ').replace('\n','')
        questionArray = qgen.getQuestions(content)
        return jsonify(questionArray)
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
