
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
#from zope.app.component.hooks import getSite
from patches import getNySite as getSite
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Acquisition import Implicit

# Product imports
from portal_tool import message_encode, message_decode
from LanguageManagers import NyLanguages

class TranslationsToolWrapper(Implicit):

    security = ClassSecurityInfo()

    def __init__(self, portal_i18n):
        self.catalog = portal_i18n.get_message_catalog()
        self.portal_i18n = portal_i18n

    security.declarePublic('get_msg_translations')
    def get_msg_translations(self, message='', lang=''):
        """
        Returns the translation of the given message in the given language.
        """
        if message == '':
            return None
        if not lang:
            lang = self.portal_i18n.get_selected_language()
        return self.catalog.gettext(message, lang, '')

    security.declarePublic('msgEncode')
    def msgEncode(self, message):
        """
        Encodes a message in order to be passed as parameter in
        the query string.
        """
        return quote(message_encode(message))

    security.declarePublic('message_encode')
    def message_encode(self, message):
        """ Encodes a message to an ASCII string.
            To be used in the user interface, to avoid problems with the
            encodings, HTML entities, etc..
        """
        return message_encode(message)

    security.declarePublic('message_decode')
    def message_decode(self, message):
        """ Decodes a message from an ASCII string.
            To be used in the user interface, to avoid problems with the
            encodings, HTML entities, etc..
        """
        return message_decode(message)

    security.declareProtected('Manage messages', 'tt_get_messages')
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

    security.declarePublic('tt_get_languages_mapping')
    def tt_get_languages_mapping(self):
        """
        Returns the languages mapping without the English language.
        Remove the entry for the 'code' = 'en'.
        """
        try:
            i18n = self.getSite().getPortalI18n()
        except AttributeError:
            i18n = getSite().getPortalI18n()
        return [{'code': x,
                 'name': i18n.get_language_name(x),
                 'default': False}
                    for x in self.catalog.get_languages() if x != 'en']

    security.declareProtected('Manage messages',
                              'tt_get_not_translated_messages_count')
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

    security.declarePublic('gettext')
    def trans(self, msg, **kwargs):
        """ Translate message and interpolate using kwargs mapping """
        lang = self.portal_i18n.get_selected_language()
        msg = self.catalog.gettext(msg, lang)
        return interpolate(msg, kwargs)

    security.declarePublic('gettext')
    def gettext(self, message, lang=None, add=1, default=None):
        if not lang:
            lang = self.portal_i18n.get_selected_language()
        return self.catalog.gettext(message, lang, default)

    security.declarePublic('gettext')
    def __call__(self, message, lang=None, add=1, default=None):
        """ use getPortalTranslations instance as gettext callable """
        return self.gettext(message, lang, add, default)

    #def __getattr__(self, name):
    #    import pdb; pdb.set_trace()
    #    return getattr(self.catalog, name)

    ## used to be in Localizer/MessageCatalog
    # In Naaya: Session messages are translated using this
    security.declarePublic('translate')
    @deprecate(("Translate method shouldn't be called on message catalog;"
                " call the translate of ITranslationDomain utility"))
    def translate(self, domain, msgid, *args, **kw):
        """This method is required to get the i18n namespace from ZPT working.
        """

        if domain is None or domain == '':
            domain = 'default'
        ut = queryUtility(ITranslationDomain, domain)
        kw['context'] = self.REQUEST
        return ut.translate(msgid, **kw)

InitializeClass(TranslationsToolWrapper)
