FROM alpine:3.7
MAINTAINER vsundar17697@outlook.com

RUN apk update
RUN apk add py3-pip
RUN pip3 install --upgrade pip \
    && pip3 install --no-cache-dir nltk==3.3 \
    Flask==1.0.2 \
    PyPDF2==1.26.0 \
    gensim==3.5.0 \
    spacy==2.0.12 \
    wikipedia==1.4.0 \
    pyemd==0.5.1 \
    && python3 -m nltk.downloader 'punkt' \
    && python3 -m spacy download en
EXPOSE 5000
# ADD ./ServerLines /server
COPY ./ServerLines /server
WORKDIR /server
CMD ["python3 YetAnotherFlaskServer.py"]