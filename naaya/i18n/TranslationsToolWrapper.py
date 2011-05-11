
# Python imports
from urllib import quote
from base64 import encodestring, decodestring
import re
import locale

# Zope imports
from zope.i18n import interpolate
from zope.i18n.interfaces import ITranslationDomain
from zope.component import queryUtility
from zope.deprecation import deprecate

# Product imports
from portal_tool import message_encode, message_decode
from LanguageManagers import NyLanguages

class TranslationsToolWrapper(object):

    def __init__(self, portal_i18n_catalog):
        self.catalog = portal_i18n_catalog

    def get_msg_translations(self, message='', lang=''):
        """
        Returns the translation of the given message in the given language.
        """
        if message == '':
            return None
        return self.catalog.gettext(message, lang, '')

    def msgEncode(self, message):
        """
        Encodes a message in order to be passed as parameter in
        the query string.
        """
        return quote(message_encode(message))

    def message_encode(self, message):
        """ Encodes a message to an ASCII string.
            To be used in the user interface, to avoid problems with the
            encodings, HTML entities, etc..
        """
        return message_encode(message)

    def message_decode(self, message):
        """ Decodes a message from an ASCII string.
            To be used in the user interface, to avoid problems with the
            encodings, HTML entities, etc..
        """
        return message_decode(message)

    def tt_get_messages(self, query, skey, rkey):
        """
        Returns a list of messages, filtered and sorted according with
        the given parameters.
         * `query` - query against the list of messages
         * `skey` - the sorting key
         * `rkey` - indicates if the list must be reversed
        """
        msgs = []
        langs = self.tt_get_languages_mapping()
        if skey == 'msg': skey = 0
        try: regex = re.compile(query.strip().lower())
        except: regex = re.compile('')
        for m, t in self.catalog.messages():
            default = t.get('en', m)
            if regex.search(default.lower()):
                if isinstance(m, unicode):
                    m = m.encode('utf-8')
                e = [m]
                i = 1
                for lang in langs:
                    if skey == lang['code']: skey = i
                    e.append(len(t.get(lang['code'], '').strip())>0)
                    i = i + 1
                msgs.append(tuple(e))
        #sort messages
        t = [(x[skey], x) for x in msgs]
        if skey == 0:
            #sort by message
            default_locale = locale.setlocale(locale.LC_ALL)
            try: locale.setlocale(locale.LC_ALL, 'en')
            except: locale.setlocale(locale.LC_ALL, '')
            t.sort(lambda x, y: locale.strcoll(x[0], y[0]))
            locale.setlocale(locale.LC_ALL, default_locale)
        else:
            #sort by translation status
            t.sort()
        if rkey: t.reverse()
        msgs = [val for (key, val) in t]
        return msgs

    def tt_get_languages_mapping(self):
        """
        Returns the languages mapping without the english language.
        Remove the entry for the 'code' = 'en'.
        """
        nylangs = NyLanguages()
        return [{'code': x,
                 'name': nylangs.get_language_name(x),
                 'default': False}
                    for x in self.catalog.get_languages() if x != 'en']

    def tt_get_not_translated_messages_count(self, query):
        """
        Returns the number of not translated messages per language.
        """
        langs = self.tt_get_languages_mapping()
        mesgs = self.tt_get_messages(query, 'msg', False)
        not_translated_messages = {}
        if len(langs) == 0 or len(mesgs) == 0:
            return False
        language = 0
        for lang in langs:
            language += 1
            mesg_count = 0
            for mesg in mesgs:
                if not mesg[language]:
                    mesg_count += 1
            not_translated_messages[lang['code']] = mesg_count
        return not_translated_messages

    def trans(self, msg, **kwargs):
        msg = self.catalog.gettext(msg)
        return interpolate(msg, kwargs)

    def __call__(self, *args, **kwargs):
        return self.catalog.gettext(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self.catalog, name)

    ## used to be in Localizer/MessageCatalog
    # In Naaya: Session messages are translated using this
    @deprecate("Translate method shouldn't be called on catalog;" +
               " call the translate of ITranslationDomain utility")
    def translate(self, domain, msgid, *args, **kw):
        """This method is required to get the i18n namespace from ZPT working.
        """

        if domain is None or domain == '':
            domain = 'default'
        ut = queryUtility(ITranslationDomain, domain)
        kw['context'] = self.REQUEST
        return ut.translate(msgid, **kw)
