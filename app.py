from flask import Flask, json, request, abort
from flask_restplus import Resource, Api
import textacy
import textacy.keyterms as tck

app = Flask(__name__)
api = Api(app)


class TextacyFormatting(object):
    """
    Format incoming data to be processed by textacy and extract keyterms.
    """
    def __init__(self, data, lang=u'fr'):
        self.data = data
        self.lang = lang
        if 'method' in data:
            self.method = data['method']
        else:
            self.method = 'sgrank'

    def _apply_keyterm_ranking(self, doc, params=None):
        if self.method == 'sgrank':
            keywords = textacy.keyterms.sgrank(doc, **params) \
                if params else tck.sgrank(doc)
        elif self.method == 'textrank':
            keywords = textacy.keyterms.textrank(doc, **params) \
                if params else tck.textrank(doc)
        elif self.method == 'singlerank':
            keywords = textacy.keyterms.singlerank(doc, **params) \
                if params else tck.singlerank(doc)
        return keywords

    def get_keyterms(self, params=None):
        try:
            txt = self.data['text'].decode('utf-8')
        except Exception as e:
            txt = self.data['text']
        print(txt)
        doc = textacy.Doc(txt, lang=self.lang)
        keywords = self._apply_keyterm_ranking(doc, params)
        return keywords


@api.route('/keywords')
class TextacyResponse(Resource):
    def post(self):
        data = request.json
        if 'text' not in data:
            abort(400, "No parameter text was founds.")
        else:
            tc = TextacyFormatting(data, lang=u'fr')
            try:
                keywords = tc.get_keyterms()
                return {'keywords': keywords}, 200
            except Exception as e:
                abort(400, e)


@api.route('/status')
class TextacyResponse(Resource):
    def get(self):
        return {'status': 'connected'}, 200



if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,debug=True)
