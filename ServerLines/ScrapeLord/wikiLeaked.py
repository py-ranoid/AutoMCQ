import wikipedia
import QuestionGenerator.PDFManip as manip
import re
from Constants import *
from nltk import sent_tokenize
from YetAnotherException import ServerError

def getRightTitle(error):
    """
    Function to return the first title rather than return error
    :param error: The error message that contains the error and the list of all the valid titles
    :return: returns a single title that is valid and which will return wikipedia content
    """
    values = getListOfTitles(error)
    try:
        return values[0]
    except IndexError as ex:
        return None

def getListOfTitles(errorStatement):
    """
    Function that returns the list of topics that could be used for the user to select.
    :param errorStatement: Error string as given by wikipedia api
    :return: List of topics
    """
    titles = errorStatement.split('\n')[1:]
    return titles

def getListOfValidTopics(topic):
    """
    For given topic, returns a list of valid topics if there are many options.
    If there aren't any valid topics, raises NO_TOPIC error.
    :param topic:
    :return: List of topics
    """
    try:
        content = wikipedia.WikipediaPage(title=topic, )
        topics = [topic]
        return topics
    except wikipedia.exceptions.DisambiguationError as ex:
        topics = getListOfTitles(str(ex))
        return topics
    except wikipedia.exceptions.PageError as ex:
        raise ServerError(NO_TOPICS)
    except Exception as ex:
        raise ServerError('New Error: ' + str(ex))

def getPageContentForFirstTopic(topic):
    """
    Given a topic, it returns the content for the wikipedia page by auto using the first valid wiki page
    :param topic: topic to quiz on
    :return: content of the wikipedia page
    """
    try:
        topics = getListOfValidTopics(topic)
        content = wikipedia.WikipediaPage(title = topics[0])
        return topic , manip.removeSlashN(content.content)
    except ServerError as ex:
        raise ex


def getTreeFromContent(content , topic):
    """
    Get the tree containing the parsed data of the wikipedia page. It gets parsed into key value pair.
    :param content: Content is the wikipedia page content
    :param topic: topic is the topic for which the quiz is on
    :return: returns the data as androidStyle which contains a dict tree and also returns the paragraph.
    """
    try:
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

    except Exception as ex:
        raise ServerError(str(ex))

def getTreeForFirstGivenTopic(topic):
    """
    function to get the information for a given topic.
    :param topic: the topic to quiz on
    :return: returns the tree for given topic, the paragraph and the updated topic name
    """
    try:
        topic, content = getPageContentForFirstTopic(topic)
        print(len(content))
        tree, para = getTreeFromContent(content, topic)
        return tree, para, topic
    except ServerError as ex:
        raise ex
    except Exception as ex:
        raise ServerError('New Error: ' + str(ex))

# print (getTreeForGivenTopic('android'))
