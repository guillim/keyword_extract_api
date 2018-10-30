FROM python:3.6

RUN pip install textacy flask flask_restplus coverage pytest pytest-cov codecov tox-travis enum34 spacy wikipedia2vec
COPY . /app
WORKDIR /app

RUN python -m spacy download fr
ENTRYPOINT ["python"]
CMD ["app.py"]
