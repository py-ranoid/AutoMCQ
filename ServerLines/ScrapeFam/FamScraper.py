from bs4 import BeautifulSoup as soup
import requests
import json
import QuestionGenerator.PDFManip as manip
SKIP_SECTIONS = [
    'Novels',
    'Explore',
]

P_TAG = 0
H2_TAG = 1
SPAN_TAG = 2
A_TAG = 3
NO_TAG = -1

class fandomContainer:
    def __init__(self , name= '' , link= '' , sub=list()):
        self.name = name
        self.link = link
        self.sub = sub
        self.content = addDataToContainer(self.link)

    def setSubTopics(self , sub):
        self.sub = sub

    def setLink(self , link):
        self.link = link

    def setName(self , name):
        self.name = name

    def printLink(self):
        print('Name: ' + self.name + ' Link: ' + self.link + ' SubTopicsLen: ' + str(len(self.sub)))

    def recursivePrintLinks(self):
        self.printLink()
        if len(self.sub) > 0:
            print('Going Deeper')
            for anyLink in self.sub:
                anyLink.recursivePrintLinks()
            print('Going Up')

    def setContent(self , content):
        self.content = content

    def getNumberSubContainers(self):
        return len(self.sub)

    def getSubContainers(self):
        return self.sub

    def getUrl(self):
        return self.link

def getALink(bs, baseUrl = ''):
    try:
        return baseUrl+bs.find('a').attrs['href']
    except AttributeError:
        try:
            return baseUrl+bs.attrs['href']
        except KeyError:
            return ''

def getSpanText(bs):
    try:
        return bs.find('span').text
    except AttributeError:
        return bs.text

def getAText(bs):
    try:
        return bs.find('a').text
    except AttributeError:
        return bs.text

def getNameFromUrl(url):
    return url.split('.')[0].split('/')[-1]

def getNavData(baseURL):
    nav_url = baseURL + "/api/v1/Navigation/Data"
    r = requests.get(nav_url)
    return r.json()

def getLinksToScrape(baseUrl, name=None):
    s = soup(requests.get(baseUrl).content,'lxml')
    allSections = s.findAll("div", {"class": "wds-tabs__tab-label wds-dropdown__toggle"})

    if name is None:
        name = getNameFromUrl(baseUrl)

    mainLink = fandomContainer(name= name, link= baseUrl)
    linkToScrape = []
    mainLink.setSubTopics([])

    for section in allSections:
        if getSpanText(section) in SKIP_SECTIONS:
            continue
        sibSection = section.find_next_sibling()
        print ("- ",getSpanText(section))
        headLink = fandomContainer(name=getSpanText(section), link= getALink(section, baseUrl))
        headLinksToScrape = []

        for subMenus in sibSection.findAll('li' , attrs={"class": "wds-dropdown-level-2"}):
            print ("\t- ",getSpanText(subMenus))
            subLink = fandomContainer(name=getSpanText(subMenus), link= getALink(subMenus, baseUrl))
            subLinksToScrape = []

            for subSubHeadings in subMenus.find('ul' , {"class": "wds-list wds-is-linked"}).findAll('a'):
                print ("\t\t- ",getSpanText(subSubHeadings))
                subSubLink = fandomContainer(name= getAText(subSubHeadings), link=getALink(subSubHeadings, baseUrl))
                subLinksToScrape.append(subSubLink)

            subLink.setSubTopics(subLinksToScrape)
            headLinksToScrape.append(subLink)

        headLink.setSubTopics(headLinksToScrape)
        linkToScrape.append(headLink)

    mainLink.setSubTopics(linkToScrape)
    mainLink.recursivePrintLinks()
    return mainLink

def getTag(content):
    content = str(content)
    if content.startswith('<p'):
        return P_TAG
    elif content.startswith('<h2'):
        return H2_TAG
    elif content.startswith('<span'):
        return SPAN_TAG
    elif content.startswith('<a'):
        return A_TAG
    else:
        return NO_TAG

def addDataToContainer(url):
    s = soup(requests.get(url).content, 'lxml')
    article = s.find("div", {"class": "WikiaArticle"})

    segContent = dict()
    curHeading = 'Default'
    curContent = ''
    for eachP in article.findAll(['p' , 'h2' , 'span']):

        tag = getTag(eachP)
        # if tag != -1:
        #     print('in ', tag , eachP.text)
        if(tag is P_TAG):
            curContent += (eachP.text + '. ')
        elif(tag is H2_TAG):
            curContent = manip.removeNewLine(curContent)
            curHeading = manip.stringifyContent(curHeading)
            curHeading = manip.removeInitialSpace(curHeading)
            curHeading = manip.removeTrailingContent(curHeading)
            segContent[curHeading] = curContent
            # print (curHeading, curContent)
            curHeading = eachP.text
            curContent = ''
        elif(tag is SPAN_TAG):
            pass
def getEpisodeNames(showname,season=1,encode=True,baseurl=""):
    url = "http://www.omdbapi.com/?t="+'+'.join(showname.split(' '))+"&apikey=54f72103&Season="+str(season)
    if encode:
        return [baseurl+'/'+i['Title'].replace(" ","_") for i in requests.get(url).json()['Episodes']]
    else:
        return [i['Title'] for i in requests.get(url).json()['Episodes']]

def legitSoup(check_url,baseUrl):
    s = soup(requests.get(check_url).content)
    finUrl = check_url
    if s.select_one(".noarticletext"):
        alt = s.select_one(".noarticletext .alternative-suggestion a")
        if alt:
            finUrl = baseUrl+alt.attrs['href']
            return soup(requests.get(finUrl).content),finUrl
        else:
            return None,"Not found"
    return s,finUrl

WIKIA_LINK = 'http://www.wikia.com/api/v1/Wikis/ByString'
HTTP_PREFIX = 'http://'
def getWikiaLink(showname):
    r = requests.post(WIKIA_LINK, data={"string": showname, "limit": "1"})
    return HTTP_PREFIX+r.json()['items'][0]['domain']


def getContainer(showname):
    baseUrl = getWikiaLink(showname)
    print (baseUrl)
    container = getLinksToScrape(baseUrl, showname)
    return container


# container = getLinksToScrape("http://dexter.wikia.com")
dContainer = getContainer('dexter')
