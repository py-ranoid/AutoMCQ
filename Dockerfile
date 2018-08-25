FROM alpine:3.7
MAINTAINER vsundar17697@outlook.com

RUN apk update
RUN apk add py3-pip
COPY ./requirements.txt /requirements.txt

RUN pip3 install --upgrade pip \
    && pip3 install --no-cache-dir -r requirements.txt \
    && python3 -m nltk.downloader 'punkt' \
    && python3 -m spacy download en

RUN rm -rf requirements.txt
COPY ./ServerLines /server
WORKDIR /server

EXPOSE 5000
ENV DB_URL=https://graphql-on-pg.herokuapp.com/v1alpha1/graphql
CMD ["python3 YetAnotherFlaskServer.py"]