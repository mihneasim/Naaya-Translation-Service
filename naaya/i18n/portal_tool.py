
# Python imports
import re
from base64 import encodestring, decodestring
from urllib import quote

# Zope imports
from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from Globals import DTMLFile
from ZPublisher import HTTPRequest
from zope.app.i18n import ZopeMessageFactory as _
from AccessControl.Permissions import view_management_screens
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# Naaya imports
from constants import ID_NAAYAI18N, TITLE_NAAYAI18N, METATYPE_NAAYAI18N

# Product imports
from LanguageManagers import (NyPortalLanguageManager, NyLanguages)
from NyMessageCatalog import LocalizerMessageCatalog
from NyNegotiator import NyNegotiator
from interfaces import INyTranslationCatalog

# used by get_namespace mainly (to prefill dtml vars)
def to_unicode(x):
    """In Zope the ISO-8859-1 encoding has an special status, normal strings
    are considered to be in this encoding by default.
    """
    if isinstance(x, unicode):
        return x
    encoding = HTTPRequest.default_encoding
    return unicode(x, encoding)

def filter_sort(x, y):
    return cmp(to_unicode(x), to_unicode(y))

def message_encode(message):
    """Encodes a message to an ASCII string.

    To be used in the user interface, to avoid problems with the
    encodings, HTML entities, etc..
    """
    if isinstance(message, unicode):
        encoding = HTTPRequest.default_encoding
        message = message.encode(encoding)

    return encodestring(message)

def message_decode(message):
    """Decodes a message from an ASCII string.

    To be used in the user interface, to avoid problems with the
    encodings, HTML entities, etc..
    """
    message = decodestring(message)
    encoding = HTTPRequest.default_encoding
    return unicode(message, encoding)

def get_url(url, batch_start, batch_size, regex, lang, empty, **kw):
    params = []
    for key, value in kw.items():
        if value is not None:
            params.append('%s=%s' % (key, quote(value)))

    params.extend(['batch_start:int=%d' % batch_start,
                   'batch_size:int=%d' % batch_size,
                   'regex=%s' % quote(regex),
                   'empty=%s' % (empty and 'on' or '')])

    if lang:
        params.append('lang=%s' % lang)

    return url + '?' + '&amp;'.join(params)


def manage_addNaayaI18n(self, languages=('en', ), REQUEST=None, RESPONSE=None):
    """
    Add a new NaayaI18n instance (portal_i18n)
    """
    self._setObject(ID_NAAYAI18N,
                    NaayaI18n(ID_NAAYAI18N, TITLE_NAAYAI18N, languages))

    if REQUEST is not None:
        RESPONSE.redirect('manage_main')

class NaayaI18n(Folder):

    meta_type = METATYPE_NAAYAI18N
    icon = 'misc_/portal_i18n/icon.gif'

    security = ClassSecurityInfo()

    def __init__(self, id, title, languages=('en', )):
        self.id = id
        self.title = title
        self._portal_langs = NyPortalLanguageManager(languages)
        catalog = INyTranslationCatalog(
                           LocalizerMessageCatalog('translation_catalog',
                                                   'Translation Catalog',
                                                   languages))
        self._catalog = catalog

    def get_negotiator(self):
        try:
            return NyNegotiator(request=self.getSite().REQUEST)
        except AttributeError:
            # maybe debug/testing environment?
            return NyNegotiator()

    def get_catalog(self):
        return self._catalog

    def get_lang_manager(self):
        if not hasattr(self, 'lang_manager'):
            self.lang_manager = NyLanguages()
        return self.lang_manager

    def get_portal_lang_manager(self):
        return self._portal_langs

    ### More specific methods:

    def get_languages_mapping(self):
        """ Returns
        [{'code': 'xx', 'name': 'Xxx xx', default: True/False}, .. ]
        for languages currently available in portal
        """
        langs = list(self._portal_langs.getAvailableLanguages())
        langs.sort()
        result = []
        default = self._portal_langs.get_default_language()
        for l in langs:
            result.append({'code': l,
                           'name': self.get_lang_manager().get_language_name(l),
                           'default': l == default})
        return result

    def add_language(self, lang):
        # add language to portal:
        self._portal_langs.addAvailableLanguage(lang)
        # and to catalog:
        self._catalog.add_language(lang)

    def del_language(self, lang):
        self._portal_langs.delAvailableLanguage(lang)
        self._catalog.del_language(lang)

    def get_selected_language(self, context=None):
        return self.get_negotiator().getLanguage(
                            self._portal_langs.getAvailableLanguages(), context)

    def change_selected_language(self, lang, goto=None, expires=None):
        """ """
        request = self.REQUEST
        response = request.RESPONSE
        negotiator = self.get_negotiator()

        # Changes the cookie (it could be something different)
        parent = self.aq_parent
        path = parent.absolute_url()[len(request['SERVER_URL']):] or '/'
        if expires is None:
            response.setCookie(negotiator.cookie_id, lang, path=path)
        else:
            response.setCookie(negotiator.cookie_id, lang, path=path,
                               expires=unquote(expires))
        # Comes back
        if goto is None:
            goto = request['HTTP_REFERER']

        response.redirect(goto)

    #######################################################################
    # Management screens
    #######################################################################
    def manage_options(self):
        """ """
        options = (
            {'label': u'Messages', 'action': 'manage_messages'},
            {'label': u'Languages', 'action': 'manage_languages'},
            {'label': u'Import', 'action': 'manage_Import_form'
             #,'help': ('Localizer', 'MC_importExport.stx')
            },
            {'label': u'Export', 'action': 'manage_Export_form'
             #,'help': ('Localizer', 'MC_importExport.stx')
            }) \
            + SimpleItem.manage_options
            #+ LanguageManager.manage_options \
        r = []
        for option in options:
            option = option.copy()
            #option['label'] = _(option['label'])
            r.append(option)
        return r

    #### Messages Tab ####

    security.declarePublic('get_namespace')
    def get_namespace(self, REQUEST):
        """For the management interface, allows to filter the messages to
        show.
        """
        # Check whether there are languages or not
        languages = self.get_languages_mapping()
        if not languages:
            return {}

        # Input
        batch_start = REQUEST.get('batch_start', 0)
        batch_size = REQUEST.get('batch_size', 15)
        empty = REQUEST.get('empty', 0)
        regex = REQUEST.get('regex', '')
        message = REQUEST.get('msg', None)

        # Build the namespace
        namespace = {}
        namespace['batch_size'] = batch_size
        namespace['empty'] = empty
        namespace['regex'] = regex

        # The language
        lang = REQUEST.get('lang', None) or languages[0]['code']
        namespace['language'] = lang

        # Filter the messages
        query = regex.strip()
        try:
            query = re.compile(query)
        except:
            query = re.compile('')

        messages = []
        for m, t in self.get_catalog().messages():
            if query.search(m) and (not empty or not t.get(lang, '').strip()):
                messages.append(m)
        messages.sort(filter_sort)
        # How many messages
        n = len(messages)
        namespace['n_messages'] = n

        # Calculate the start
        while batch_start >= n:
            batch_start = batch_start - batch_size
        if batch_start < 0:
            batch_start = 0
        namespace['batch_start'] = batch_start
        # Select the batch to show
        batch_end = batch_start + batch_size
        messages = messages[batch_start:batch_end]
        # Batch links
        namespace['previous'] = get_url(REQUEST.URL, batch_start - batch_size,
            batch_size, regex, lang, empty)
        namespace['next'] = get_url(REQUEST.URL, batch_start + batch_size,
            batch_size, regex, lang, empty)

        # Get the message
        message_encoded = None
        #translations = {}
        translation = None
        if message is None:
            if messages:
                message = messages[0]
                #translations = self.get_translations(message)
                translation = self.get_catalog().gettext(message, lang, '')
                message = to_unicode(message)
                message_encoded = message_encode(message)
        else:
            message_encoded = message
            message = message_decode(message_encoded)
            #translations = self.get_translations(message)
            translation = self.get_catalog().gettext(message, lang, '')
            message = to_unicode(message)
        namespace['message'] = message
        namespace['message_encoded'] = message_encoded
        #namespace['translations'] = translations
        namespace['translation'] = translation

        # Calculate the current message
        namespace['messages'] = []
        for x in messages:
            x = to_unicode(x)
            x_encoded = message_encode(x)
            url = get_url(
                REQUEST.URL, batch_start, batch_size, regex, lang, empty,
                msg=x_encoded)
            namespace['messages'].append({
                'message': x,
                'message_encoded': x_encoded,
                'current': x == message,
                'url': url})

        # The languages
        for language in languages:
            code = language['code']
            language['name'] = _(language['name'])
            language['url'] = get_url(REQUEST.URL, batch_start, batch_size,
                regex, code, empty, msg=message_encoded)
        namespace['languages'] = languages

        return namespace

    security.declareProtected('Manage messages', 'manage_messages')
    manage_messages = DTMLFile('zpt/messages', globals())

    security.declareProtected('Manage messages', 'manage_editMessage')
    def manage_editMessage(self, message, language, translation,
                           REQUEST, RESPONSE):
        """Modifies a message.
        """
        message_encoded = message
        message = message_decode(message_encoded)
        message_key = self.get_catalog()._get_message_key(message)
        self.get_catalog().edit_message(message_key, language, translation)

        url = get_url(REQUEST.URL1 + '/manage_messages',
                      REQUEST['batch_start'], REQUEST['batch_size'],
                      REQUEST['regex'], REQUEST.get('lang', ''),
                      REQUEST.get('empty', 0),
                      msg=message_encoded,
                      manage_tabs_message=_(u'Saved changes.'))
        RESPONSE.redirect(url)

    security.declareProtected('Manage messages', 'manage_delMessage')
    def manage_delMessage(self, message, REQUEST, RESPONSE):
        """ """
        message = message_decode(message)
        message_key = self.get_catalog()._get_message_key(message)
        self.get_catalog().del_message(message_key)

        url = get_url(REQUEST.URL1 + '/manage_messages',
                      REQUEST['batch_start'], REQUEST['batch_size'],
                      REQUEST['regex'], REQUEST.get('lang', ''),
                      REQUEST.get('empty', 0),
                      manage_tabs_message=_(u'Saved changes.'))
        RESPONSE.redirect(url)

    #### Languages Tab ####

    security.declareProtected(view_management_screens, 'manage_languages')
    manage_languages = PageTemplateFile('zpt/languages', globals())

    security.declareProtected(view_management_screens, 'manage_addLanguage')
    def manage_addLanguage(self, language, REQUEST=None):
        """
        Add a new language for this portal.
        """
        self.getSite().gl_add_site_language(language)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_languages?save=ok')

    security.declareProtected(view_management_screens, 'manage_delLanguages')
    def manage_delLanguages(self, languages, REQUEST=None):
        """
        Delete one or more languages.
        """
        self.getSite().gl_del_site_languages(languages)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_languages?save=ok')

    security.declareProtected(view_management_screens, 'manage_changeDefaultLang')
    def manage_changeDefaultLang(self, language, REQUEST=None):
        """
        Change the default portal language.
        """
        self.getSite().gl_change_site_defaultlang(language)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_languages?save=ok')