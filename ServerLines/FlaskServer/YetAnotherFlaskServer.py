from flask import Flask, request , jsonify
import QuestionGenerator.PDFManip as manip
import ScrapeLord.wikiLeaked as wiki
app = Flask(__name__)
PAGE_NUMBER = 'pageNumber'

pdf_stored = None
custom_content = None
wiki_content = None

CUSTOM_CONTENT = 'custom'
PDF_FILE = 'pdf'
SUCCESS = 'Success'
FAILURE = 'Failure'
TOPIC = 'topic'

def resetContents():
    custom_content = None
    wiki_content = None
    pdf_stored = None

@app.route('/getPageQuestion', methods=['POST'])
def getPageQuestion():
    req = request.get_json()
    pageNumber = req[PAGE_NUMBER]
    textContent = manip.getPageContent(pageNumber , None)
    textContent = manip.removeSlashN(textContent)

    return jsonify(textContent)

@app.route('/getPdf', methods=['POST'])
def getPdfAndStore():
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

@app.route('/getContentForCustomContent', methods=['POST'])
def getContentForCustomContent():
    req = request.get_json()
    resetContents()
    custom_content = req[CUSTOM_CONTENT]
    # Train word2vec here



if __name__ == '__main__':
    app.run(debug=True,use_reloader=False) #run app in debug mode on port 5000