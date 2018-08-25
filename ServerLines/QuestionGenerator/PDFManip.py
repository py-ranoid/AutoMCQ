import PyPDF2
import re

DEFAULT_FILE = 'temp.pdf'

def performSmartCorrections(content):
    # content = re.sub(r'([a-zA-Z])\.([a-zA-Z0-9])' , r'\1. \2' , content)
    content = content.replace('\"' , '')
    content = content.replace('"' , '')
    # print(content)
    return content

def removeSlashN(content):
    content = unicode(content)
    content = content.replace('\r\n',' ')
    content = content.replace('\n' , ' ')
    content = re.sub(r' +' , ' ' , content)
    # content = performSmartCorrections(content)
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
