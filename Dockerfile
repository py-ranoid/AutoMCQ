FROM python:3.6
MAINTAINER vsundar17697@outlook.com
RUN pip install wikipedia \
    && pip install spacy \
    && pip install flask \
    && pip install PyPDF2 \
    && pip install nltk \
    && python -m nltk.downloader 'punkt' \
    && python -m spacy download en \
    && pip install gensim
EXPOSE 5000
# ADD ./ServerLines /server
COPY ./ServerLines /server
WORKDIR /server
CMD ["python YetAnotherFlaskServer.py"]