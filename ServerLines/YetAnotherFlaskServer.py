from flask import Flask, request , jsonify
import QuestionGenerator.PDFManip as manip
import ScrapeLord.wikiLeaked as wiki
import QuestionGenerator.Qgen as qgen

app = Flask(__name__)
PAGE_NUMBER = 'pageNumber'

pdf_stored = None
wiki_content = None

CUSTOM_CONTENT = 'content'
PDF_FILE = 'pdf'
SUCCESS = 'Success'
FAILURE = 'Failure'
TOPIC = 'topic'
QUESTIONS = 'questions'

def resetContents():
    wiki_content = None
    pdf_stored = None


@app.route('/getQuestionsForPdf', methods=['POST'])
def getQuestionsForPdf():
    req = request.get_json()
    pageNumber = req[PAGE_NUMBER]
    textContent = manip.getPageContent(pageNumber , None)
    questionsArray = qgen.getQuestions(textContent)
    resp = {}
    resp[PAGE_NUMBER] = pageNumber
    resp[QUESTIONS] = questionsArray
    return jsonify(resp)

@app.route('/getContentForPdf', methods=['POST'])
def getContentForPdf():
    try:
        resetContents()
        pdf_stored = request.files[PDF_FILE]
        #Train word to vec here
        return jsonify(SUCCESS)
    except Exception as ex:
        print(ex)
        return jsonify(FAILURE)

@app.route('/getContentForTopic', methods=['POST'])
def getContentForTopic():
    req = request.get_json()
    topic = req[TOPIC]
    resetContents()
    content_tree , wiki_content = wiki.getTreeForGivenTopic(topic)
    content_tree[TOPIC] = topic
    #train word to vec here
    return jsonify(content_tree)

@app.route('/getQuestionsForText', methods=['POST'])
def getQuestionsForText():
    req = request.get_json()
    content = req[CUSTOM_CONTENT]
    questionArray = qgen.getQuestions(content)
    resp = {}
    resp[QUESTIONS] = questionArray
    return jsonify(resp)


if __name__ == '__main__':
    app.run(debug=True,use_reloader=False) #run app in debug mode on port 5000