FROM python:3.6

RUN pip install textacy flask flask_restplus flask-cors  spacy
COPY . /app
WORKDIR /app

RUN python -m spacy download fr
ENTRYPOINT ["python"]
CMD ["app.py"]
