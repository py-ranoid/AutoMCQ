FROM alpine:3.6
MAINTAINER vsundar17697@outlook.com

RUN apk update \
    && apk add py3-pip \
    && pip install --no-cache-dir -r requirements.txt \
    && python -m nltk.downloader 'punkt' \
    && python -m spacy download en \
EXPOSE 5000
# ADD ./ServerLines /server
COPY ./ServerLines /server
WORKDIR /server
CMD ["python YetAnotherFlaskServer.py"]