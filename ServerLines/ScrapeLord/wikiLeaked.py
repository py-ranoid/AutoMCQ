import wikipedia
import QuestionGenerator.PDFManip as manip
import re
import QuestionGenerator.PDFManip as manip

def getRightTitle(error):
    values = error.split('\n')
    return values[1]

def getPageContent(topic):
    try:
        content = wikipedia.WikipediaPage(title= topic, )
        return manip.removeSlashN(content.content)
    except Exception as ex:
        print('Error: ' , str(ex))
        return getPageContent(getRightTitle(str(ex)))


def getTreeFromContent(content):
    content = re.sub(r'(={3,8})(.+)(={3,8})' , ' ' , content)
    content = manip.removeSlashN(content)
    allTopics = content.split(' == ')

    wikiContent = {}
    wikiContent['Introduction'] = allTopics[0]
    i = 1
    while i < len(allTopics) - 1:
        if(len(allTopics[i]) >= 3 and len(allTopics[i+1]) >= 10 ):
            value = manip.removeSlashN(allTopics[i+1]).replace('\"','')
            if len(value)>200:
                wikiContent[allTopics[i].replace("=",'').strip()] = value
        i+=2

    paragraph = ''
    for key , value in wikiContent.items():
        paragraph += value
        paragraph += '. '
        print(key ,': ', value)

    return wikiContent , paragraph

def getTreeForGivenTopic(topic):
    content = getPageContent(topic)
    tree , para = getTreeFromContent(content)
    return tree , para


# getTreeForGivenTopic('cryptocurrency')
