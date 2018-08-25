from flask import Flask, request , jsonify
import QuestionGenerator.PDFManip as manip
import ScrapeLord.wikiLeaked as wiki
import QuestionGenerator.Qgen as qgen
from DBops.crud import insert,get_query
import time

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
    # print (textContent)
    questionsArray = qgen.getQuestions(textContent)
    resp = {}
    print (questionsArray)
    return jsonify(questionsArray)

@app.route('/getContentForPdf', methods=['POST'])
def getContentForPdf():
    print ('Storing file')
    request.files['file'].save(manip.DEFAULT_FILE)
    return jsonify({"status":"success"})

@app.route('/getContentForTopic', methods=['POST'])
def getContentForTopic():
    topic = request.form[TOPIC].replace('\r\n',' ').replace('\n','')
    UID = request.form['uid'].replace('\r\n',' ').replace('\n','')
    init_time = time.time()
    resetContents()
    resp = insert(UID,'TOPI2QUIZ',"LENGTH"+"::"+str(len(topic))+"::"+topic)
    print (resp)
    print ("INS_time :",time.time()-init_time)
    content_tree , wiki_content = wiki.getTreeForGivenTopic(topic)
    print ("CON_time :".time.time()-init_time)
    # print (content_tree)
    #train word to vec here
    return jsonify(content_tree)

@app.route('/getQuestionsForText', methods=['POST'])
def getQuestionsForText():
    content = request.form['content'].replace('\r\n',' ').replace('\n','')
    UID = request.form['uid'].replace('\r\n',' ').replace('\n','')
    init_time = time.time()
    resp = insert(UID,'TEXT2QUIZ',"LENGTH"+"::"+str(len(content))+"::"+content[:20])
    print (resp)
    print ("INS_time :",time.time()-init_time)
    #print (get_query(UID,'TEXT2QUIZ'+"::"+"LENGTH"+"::"+str(len(content))+"::"+content[:20]))
    questionArray = qgen.getQuestions(content)
    print ("QUE_time :",time.time()-init_time)
    # print (questionArray)
    # resp = {}
    # resp[QUESTIONS] =
    return jsonify(questionArray)


if __name__ == '__main__':
    app.run(debug=True,
            use_reloader=False,
            host='0.0.0.0'
            ) #run app in debug mode on port 5000
