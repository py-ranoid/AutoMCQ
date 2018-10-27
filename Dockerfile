FROM python:3.6-alpine as base
MAINTAINER vsundar17697@outlook.com

FROM base as builder
RUN mkdir /install
WORKDIR /install
COPY ./requirements.txt /requirements.txt
RUN pip install --install-option="--prefix=/install" -r /requirements.txt \
    && python3 -m nltk.downloader 'punkt' \
    && python3 -m spacy download en

FROM base
COPY --from=builder /install /usr/local
COPY ./ServerLines /server
WORKDIR /server

EXPOSE 5000
ENV DB_URL=https://graphql-on-pg.herokuapp.com/v1alpha1/graphql
CMD ["python3 YetAnotherFlaskServer.py"]