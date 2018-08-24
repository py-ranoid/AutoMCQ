FROM alpine:3.6
MAINTAINER vsundar17697@outlook.com

RUN apk update \
    && apk add py3-pip \
    && pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt \
    && python3 -m nltk.downloader 'punkt' \
    && python3 -m spacy download en
EXPOSE 5000
# ADD ./ServerLines /server
COPY ./ServerLines /server
WORKDIR /server
CMD ["python3 YetAnotherFlaskServer.py"]