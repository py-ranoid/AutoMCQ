import PyPDF2
import re
import sys
from unidecode import unidecode
DEFAULT_FILE = 'temp.pdf'

def removeNonAsciiCharacters(content):
    content = unidecode(content)
    content = re.sub(r'[^\x00-\x7F]+', ' ', content)
    return content

def stringifyContent(content):
    if sys.version_info[0]  < 3:
        content = unicode(content)
        content = removeNonAsciiCharacters(content)
    else:
        content = str(content)
        content = removeNonAsciiCharacters(content)
    return content

def removeSlashN(content):
    content = stringifyContent(content)
    content = re.sub(r'\n' , ' ' , content)
    content = re.sub(r' +' , ' ' , content)
    return content

def removeSlashQuotes(content):
    content = stringifyContent(content)
    content = content.replace('\"', ' ')
    content = re.sub(r' +', ' ', content)
    content = removeInitialSpace(content)
    return content

def removeInitialSpace(content):
    if content[0] == ' ':
        content = content[1:]
    return content

def removeTrailingContent(content):
    while(True):
        if content[-1] == ' ':
            content = content[:-1]
        elif content[-1] == '.':
            content = content[:-1]
        elif content[-1] == '_':
            content = content[:-1]
        elif content[-1] == '-':
            content = content[:-1]
        else:
            break
    return content

def getPdfFileObject(pdf):
    pdfReader = None
    if(pdf == None):
        pdfFileObj = open(DEFAULT_FILE, 'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    else:
        pdfReader = PyPDF2.PdfFileReader(pdf)
    return pdfReader

def getCompletePdf(pdf):
    pdfReader = PyPDF2.PdfFileReader(pdf)
    numPages = pdfReader.numPages
    content = ''
    curPage = 1
    while curPage < numPages:
        content += removeSlashN(pdfReader.getPage(curPage).extractText())
    return content

def getPageContent(pageNumber , pdf):
    pdfReader = getPdfFileObject(pdf)
    content = pdfReader.getPage(pageNumber)
    text = removeSlashN(content.extractText())
    # print(text)
    return text

# performSmartCorrections('ggwp.well played.nonono.6.9. This is awesome " \' " he said')
