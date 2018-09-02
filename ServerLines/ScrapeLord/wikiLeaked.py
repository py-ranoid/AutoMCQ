import wikipedia
import QuestionGenerator.PDFManip as manip
import re
from Constants import *
from nltk import sent_tokenize
from YetAnotherException import ServerError

def getRightTitle(error):
    values = error.split('\n')
    print(values)
    try:
        return values[1]
    except IndexError as ex:
        return None

def getPageContent(topic):
    try:
        content = wikipedia.WikipediaPage(title= topic, )
        return topic, manip.removeSlashN(content.content)
    except wikipedia.exceptions.DisambiguationError as ex:
        nextTitle = getRightTitle(str(ex))
        if nextTitle != None:
            topic, content = getPageContent(nextTitle)
            return topic, content
        else:
            raise ServerError(str(ex))
    except wikipedia.exceptions.PageError as ex:
        raise ServerError(str(ex))



def getTreeFromContent(content , topic):
    content = manip.removeSlashN(content)
    allTopics = content.split(' == ')

    wikiContent = {}
    wikiContent['Introduction'] = allTopics[0]
    i = 1
    while i < len(allTopics) - 1:
        if(len(allTopics[i]) >= 3 and len(allTopics[i+1]) >= 10 ):
            value = manip.removeSlashN(allTopics[i+1]).replace('\"','')
            if len(value)>200:
                wikiContent[allTopics[i].replace("=",'').strip()] = re.sub(r'(={1,10})(.+)(={1,10})' , ' ' ,value).strip()
        i+=2

    paragraph = ''
    androidStyle = []
    sent_count = 0
    for key , value in wikiContent.items():
        paragraph += value
        paragraph += '. '
        num_sent = len(sent_tokenize(value))
        if num_sent >= MINIMUM_LENGTH_SUB_TOPIC:
            androidStyle.append({
                'topicName': key,
                'topicContent': value
            })
        sent_count += num_sent

    if sent_count <= MINIMUM_LENGTH_TOPIC:
        androidStyle = []
        androidStyle.append({
            'topicName': topic,
            'topicContent': paragraph
        })

    return androidStyle, paragraph

def getTreeForGivenTopic(topic):
    try:
        topic, content = getPageContent(topic)
        print(len(content))
        tree, para = getTreeFromContent(content, topic)
        return tree, para, topic
    except ServerError as ex:
        raise ex
    except Exception as ex:
        raise ServerError('New Error: ' + str(ex))

# print (getTreeForGivenTopic('android'))
