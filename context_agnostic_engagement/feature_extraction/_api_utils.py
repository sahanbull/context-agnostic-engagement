import time

import requests
import ujson as json

ERROR_KEY = u'error'
STATUS_FIELD = u'status'

URL_FIELD = u'url'
PAGERANK_FIELD = u'pageRank'

COSINE_FIELD = u'cosine'

ANNOTATION_DATA_FIELD = u'annotation_data'

_WIKIFIER_URL = u"http://www.wikifier.org/annotate-article"
_WIKIFIER_MAX_SERVER_LIMIT = 25000
WIKIFIER_MAX_CHAR_CEILING = round(_WIKIFIER_MAX_SERVER_LIMIT * .99)  # 99% of max allowed num chars for a post request


def _get_wikififier_concepts(resp):
    annotations = [{URL_FIELD: ann[URL_FIELD],
                    COSINE_FIELD: ann[COSINE_FIELD],
                    PAGERANK_FIELD: ann[PAGERANK_FIELD]} for ann in resp.get("annotations", [])]

    return {
        ANNOTATION_DATA_FIELD: annotations,
        STATUS_FIELD: resp[STATUS_FIELD]
    }


def _get_wikifier_response(text, api_key, df_ignore, words_ignore):
    params = {"text": text,
              "userKey": api_key,
              "nTopDfValuesToIgnore": df_ignore,
              "nWordsToIgnoreFromList": words_ignore}
    r = requests.post(_WIKIFIER_URL, params)
    if r.status_code == 200:
        resp = json.loads(r.content)
        if ERROR_KEY in resp:
            raise ValueError("error in response : {}".format(resp[ERROR_KEY]))
        return resp
    else:
        raise ValueError("http status code 200 expected, got status code {} instead".format(r.status_code))


def wikify(text, key, df_ignore, words_ignore):
    """This function takes in a text representation of a lecture transcript and associates relevant Wikipedia topics to
    it using www.wikifier.org entity linking technology.

    Args:
        text (str): text that needs to be Wikified (usually lecture transcript string)
        key (str): API key for Wikifier obtained from http://www.wikifier.org/register.html
        df_ignore (int): Most common words to ignore based on Document frequency
        words_ignore (int): Most common words to ignore based on Term frequency

    Returns:
        [{key:val}]: a dict with status of the request and the list of Wiki topics linked to the text
    """
    try:
        resp = _get_wikifier_response(text, key, df_ignore, words_ignore)
        resp[STATUS_FIELD] = 'success'
    except ValueError as e:
        try:
            STATUS_ = e.message
        except:
            STATUS_ = e.args[0]
        return {
            STATUS_FIELD: STATUS_
        }
    time.sleep(0.5)
    return _get_wikififier_concepts(resp)
