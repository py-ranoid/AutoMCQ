from flask import Flask, request , jsonify
import QuestionGenerator.PDFManip as manip
import ScrapeLord.wikiLeaked as wiki
import QuestionGenerator.Qgen as qgen

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
    # req = request.get_json()
    # pageNumber = int(req[PAGE_NUMBER])
    pageNumber = int(request.form[PAGE_NUMBER].replace('\r\n',' ').replace('\n','')) - 1
    print (pageNumber)
    textContent = manip.getPageContent(pageNumber , None)
    print (textContent)
    questionsArray = qgen.getQuestions(textContent)
    resp = {}
    # resp[PAGE_NUMBER] = pageNumber
    # resp[QUESTIONS] = questionsArray
    print (questionsArray)
    return jsonify(questionsArray)

@app.route('/getContentForPdf', methods=['POST'])
def getContentForPdf():
    print ('Storing file')
    request.files['file'].save(manip.DEFAULT_FILE)
    return jsonify({"status":"success"})

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
    content = request.form['content'].replace('\r\n',' ').replace('\n','')
    questionArray = qgen.getQuestions(content)
    # print (questionArray)
    # resp = {}
    # resp[QUESTIONS] =
    return jsonify(questionArray)


if __name__ == '__main__':
    app.run(debug=True,
            use_reloader=False,
            host='0.0.0.0'
            ) #run app in debug mode on port 5000
