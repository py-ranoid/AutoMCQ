from flask import Flask, request ,jsonify

app = Flask(__name__)
time_left = 0

@app.route('/addTime', methods=['POST'])
def addTime():
    global time_left
    score = request.form.get('score')
    # score = int(request.form['score'].replace('\r\n',' ').replace('\n',''))
    if int(score) > 70:
        time_left += 1
    return "SUCCESS"

@app.route('/getTime', methods=['GET'])
def getTime():
    global time_left
    return "TV hours left :"+str(time_left)

if __name__ == '__main__':
    app.run(debug=True,
            use_reloader=False,
            host='0.0.0.0',
            port=5555,
            ) #run app in debug mode on port 5000
