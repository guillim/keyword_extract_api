from flask import Flask, json, request, abort
from flask_restplus import Resource, Api, fields
from flask_cors import CORS
import textacy
import textacy.keyterms as tck
import os

app = Flask(__name__)
# cors = CORS(app, resources={r"/*": {"origins": r"/*"}})
cors = CORS(app, resources={r"/*": {"origins": r"^http.*(dontgomanual.com|keyword-extract-app.herokuapp.com)"}})
api = Api(app, version='1.0', title='keywords_extract',description='API for keywords extraction', doc='/documentation/')


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
        doc = textacy.make_spacy_doc(txt, lang=self.lang)
        keywords = self._apply_keyterm_ranking(doc, params)
        return keywords


resource_keywords_params = api.model('keywordsParamsInput', {
    'normalize': fields.String(description='if you want to normalize your words. "lemma" is default, null is recommended at first', enum=['lemma', 'lower', False], example= 'lemma'),
    'n_keyterms': fields.Integer(description='number of keywords the API will return (sorted by relevance) - default to 10', example= 3),
    'ngrams': fields.Integer(description='number of words that count as results - default to all, remove this for all', example= 3)
})

resource_keywords = api.model('keywordsInput', {
    'method': fields.String(required=True, description='a method for ranking the keywords. can be sgrank, textrank or singlerank',enum=['sgrank', 'textrank', 'singlerank'], example= 'sgrank'),
    # 'method': fields.Integer(description='The unique identifier of a blog post'),
    'params': fields.Nested(resource_keywords_params),
    # 'params': fields.String(required=True, description='parameters for the use of the method previously defined. There are two parameter: normalize - if you want to lemma your words for instance -  & n_keyterms - if you want specific n_grams to be looked after', example= '{"normalize":null,"n_keyterms":3}'),
    'text': fields.String(required=True, description='the text you want ot extract keywords from',example= 'Paris is a nice city to live in. I like New york as well, but Paris has a charm you cannot find elsewhere')
})

@api.route('/keywords')
@api.expect(resource_keywords)
class TextacyResponse(Resource):
    def post(self):
        data = request.json
        params = data.get('params')
        if 'text' not in data:
            abort(400, "No parameter text was founds.")
        else:
            tc = TextacyFormatting(data, lang=u'fr')
            try:
                keywords = tc.get_keyterms(params=params)
                return {'keywords': keywords}, 200
            except Exception as e:
                abort(400, e)


@api.route('/status')
@api.doc(params={})
class TextacyResponse(Resource):
    def get(self):
        return {'status': 'connected'}, 200


ON_HEROKU = os.environ.get('ON_HEROKU')
# print('ON_HEROKU=',ON_HEROKU)
if ON_HEROKU:
    port = int(os.environ.get('PORT', 5000))
else:
    port = 5000

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=port,debug=True)
