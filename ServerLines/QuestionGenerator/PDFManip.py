import PyPDF2
import re
import sys

DEFAULT_FILE = 'temp.pdf'

def performSmartCorrections(content):
    content = content.replace('\"' , '')
    content = content.replace('"' , '')
    content = removeSlashN(content)
    return content

def removeSlashN(content):
    if sys.version_info[0]  < 3:
        content = unicode(content)
    else:
        content = str(content)
    content = content.replace('\r\n',' ')
    content = content.replace('\n' , ' ')
    content = re.sub(r' +' , ' ' , content)
    return content

def removeSlashQuotes(content):
    if sys.version_info[0]  < 3:
        content = unicode(content)
    else:
        content = str(content)
    content = content.replace('\"', ' ')
    content = re.sub(r' +', ' ', content)
    content = removeInitialSpace(content)
    return content

def removeInitialSpace(content):
    if content[0] == ' ':
        content = content[1:]
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
