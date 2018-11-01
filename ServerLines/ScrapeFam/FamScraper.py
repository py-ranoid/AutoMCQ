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

SCRAPE = False
class fandomContainer:
    def __init__(self , name= '' , link= '' , sub=list()):
        global SCRAPE
        self.name = name
        self.link = link
        self.sub = sub
        self.all_links = set([])
        if SCRAPE:
            self.content = addDataToContainer(self.link)
        else:
            self.content = ""
    
    def populate(self):
            self.content = addDataToContainer(self.link)

    def toJSON(self,fname):
        all_content = self.getAllContent()
        with open(fname,'w') as f:                                                 
            f.write(json.dumps(all_content))

    def getAllContent(self):
        all_content = {"content":self.content,"link":self.link}
        for a in self.sub:
            all_content[a.name]={'content':a.content,'link':a.link}
            for b in a.sub:
                all_content[a.name][b.name] = {"content":b.content,"link":b.link}
                for c in b.sub:
                    all_content[a.name][b.name][c.name] = {"content":c.content,"link":c.link}
        return all_content
    
    def getIndexedContent(self):
        all_content = {"content":self.content,"link":self.link}
        for ia,a in enumerate(self.sub):
            all_content[str(ia)+'::'+a.name]={'content':a.content,'link':a.link}
            for ib,b in enumerate(a.sub):
                all_content[str(ia)+'::'+a.name][str(ib)+'::'+b.name] = {"content":b.content,"link":b.link}
                for ic,c in enumerate(b.sub):
                    all_content[str(ia)+'::'+a.name][str(ib)+'::'+b.name][str(ic)+"::"+c.name] = {"content":c.content,"link":c.link}
        return all_content
    def setSubTopics(self , sub):
        self.sub = sub

    def getSeasonLinks(self):
        return [i for i in self.all_links if '/Season' in i]

    def setLink(self , link):
        self.link = link

    def setName(self , name):
        self.name = name

    def printLink(self):
        # print('Name: ' + self.name + ' Link: ' + self.link + ' SubTopicsLen: ' + str(len(self.sub)))
        pass

    def recursivePrintLinks(self):
        self.printLink()
        if len(self.sub) > 0:
            # print('Going Deeper')
            for anyLink in self.sub:
                anyLink.recursivePrintLinks()
            # print('Going Up')

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
        mainLink.all_links.add(getALink(section, baseUrl))
        headLink = fandomContainer(name=getSpanText(section), link= getALink(section, baseUrl))
        headLinksToScrape = []

        for subMenus in sibSection.findAll('li' , attrs={"class": "wds-dropdown-level-2"}):
            print ("\t- ",getSpanText(subMenus))
            mainLink.all_links.add(getALink(subMenus, baseUrl))
            subLink = fandomContainer(name=getSpanText(subMenus), link= getALink(subMenus, baseUrl))
            subLinksToScrape = []

            for subSubHeadings in subMenus.find('ul' , {"class": "wds-list wds-is-linked"}).findAll('a'):
                print ("\t\t- ",getSpanText(subSubHeadings))
                mainLink.all_links.add(getALink(subSubHeadings, baseUrl))
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

def addDataToContainer(url=None,s=None):
    if s is None:
        s = soup(requests.get(url).content, 'lxml')
    article = s.find("div", {"class": "WikiaArticle"})

    segContent = dict()
    curHeading = 'Default'
    curContent = ''
    for eachP in article.findAll(['p' , 'h2' , 'span','a']):
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
    return segContent

def getEpisodeNames(showname,season=1,encode=True,baseurl=""):
    url = "http://www.omdbapi.com/?t="+'+'.join(showname.split(' '))+"&apikey=54f72103&Season="+str(season)
    if encode:
        return [(i['Title'],baseurl+'/'+i['Title'].replace(" ","_")) for i in requests.get(url).json()['Episodes']]
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

"""
GoT Content Scraper
SCRAPE = True
gContainer = getContainer('game of thrones') 
gContainer.sub[2].sub += gContainer.sub[2].sub[3].sub
for ind in range(1,6):
    print ("- Season",ind)
    for ep in getEpisodeNames('game of thrones',ind,baseurl=gContainer.link):
        print ("\t- Episode",ep[0])
        s,ep_url = legitSoup(ep[1],gContainer.link)
        if s is not None:
            epContainer = fandomContainer(name= ep[0], link=ep_url)
            gContainer.sub[2].sub[-5:][ind-1].sub.append(epContainer)
"""
# container = getLinksToScrape("http://dexter.wikia.com")
SCRAPE = False
dContainer = getContainer('dexter')
