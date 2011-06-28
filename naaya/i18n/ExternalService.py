
# Python imports
try:
    import json
except ImportError:
    import simplejson as json
import urllib2
from urllib import urlencode
import re

DUMMY_TEXT = "'XXXXX'" # google tends to change other wildcards like ${}
REQUEST_URI = 'http://translate.google.com/translate_a/t'

def external_translate(message, target_lang):
    """
    Call Google Translate as a regular Http Agent, return translation
    if everything went ok. Google Translate API is going to be
    shut down on 1st Dec 2011, can not rely on that one.

    Method only used for suggesting translations to translation managers.

    """
    try:
        op = urllib2.build_opener()
        op.addheaders = [('User-agent', 'Mozilla/5.0')]
        handler = op.open(REQUEST_URI,
                          urlencode({'client': 't', 'text': message,
                                     'sl': 'en', 'tl': target_lang}))
        body = handler.read()
        # Response is not exactly a json
        jsonize_pat = re.compile(',,')
        while jsonize_pat.search(body) is not None:
            body = jsonize_pat.sub(r',"",', body)
        # Replace mappings, if any
        mappings_pat = re.compile(r'\$\{(.*?)\}')
        mappings = mappings_pat.findall(body)
        if mappings is not []:
            mappings_pat.sub(DUMMY_TEXT, body)

        json_data = json.loads(body)

        try:
            translation = json_data[0][0][0]
        except KeyError:
            # no translation or unexpected response
            return ''
        else:
            if mappings is not []:
                for m in mappings:
                    translation = translation.replace(DUMMY_TEXT, "${"+m+"}", 1)
            return translation

    except Exception:
        ### Google translate should fall silently, not a critical functionality
        return ''
