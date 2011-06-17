
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
from LanguageManagers import NyPortalLanguageManager, NyLanguages
from LanguageManagers import normalize_code
from NyMessageCatalog import NyMessageCatalog
from NyNegotiator import NyNegotiator
from interfaces import INyTranslationCatalog
from ImportExport import TranslationsImportExport

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


def manage_addNaayaI18n(self, languages=[('en', 'English')],
                        REQUEST=None, RESPONSE=None):
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

    def __init__(self, id, title, languages=[('en', 'English')]):
        self.id = id
        self.title = title
        n_languages = []
        for (code, name) in languages:
            n_languages.append((normalize_code(code), name))
        self._portal_langs = NyPortalLanguageManager(n_languages)
        lang_codes = tuple([x[0] for x in n_languages])
        catalog = NyMessageCatalog('translation_catalog', 'Translation Catalog',
                                    lang_codes)
        self._catalog = catalog

    def get_negotiator(self):
        try:
            return NyNegotiator(request=self.getSite().REQUEST)
        except AttributeError:
            # maybe debug/testing environment?
            return NyNegotiator()

    def get_message_catalog(self):
        return self._catalog

    def get_lang_manager(self):
        if not hasattr(self, 'lang_manager'):
            self.lang_manager = NyLanguages()
        return self.lang_manager

    def get_portal_lang_manager(self):
        return self._portal_langs

    def get_importexport_tool(self):
        return TranslationsImportExport(self.get_message_catalog())

    ### More specific methods:
    def get_language_name(self, code):
        if code in self.get_portal_lang_manager().getAvailableLanguages():
            # try to get name from added langs to site
            return self.get_portal_lang_manager().get_language_name(code)
        else:
            # not there, default to NyLanguages: loads the large languages.txt
            return self.get_lang_manager().get_language_name(code)

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
                           'name': self.get_language_name(l),
                           'default': l == default})
        return result

    def add_language(self, lang_code, lang_name=None):
        if not lang_code:
            raise ValueError('No language code provided')
        lang_code = normalize_code(lang_code)
        if lang_name is None:
            # search for name directly in languages.txt, obviously not in site
            lang_name = self.get_lang_manager().get_language_name(lang_code)
        # add language to portal:
        self._portal_langs.addAvailableLanguage(lang_code, lang_name)
        # and to catalog:
        self._catalog.add_language(lang_code)

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
            {'label': u'Import', 'action': 'manage_import'
             #,'help': ('Localizer', 'MC_importExport.stx')
            },
            {'label': u'Export', 'action': 'manage_export'
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
        for m, t in self.get_message_catalog().messages():
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
                translation = self.get_message_catalog()\
                                  .gettext(message, lang, '')
                message = to_unicode(message)
                message_encoded = message_encode(message)
        else:
            message_encoded = message
            message = message_decode(message_encoded)
            #translations = self.get_translations(message)
            translation = self.get_message_catalog().gettext(message, lang, '')
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
        message_key = message_decode(message_encoded)
        self.get_message_catalog()\
            .edit_message(message_key, language, translation)

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
        message_key = message_decode(message)
        self.get_message_catalog().del_message(message_key)

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
    def manage_addLanguage(self, language_code, language_name, REQUEST=None):
        """
        Add a new language for this portal.
        """
        self.getSite().gl_add_site_language(language_code, language_name)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_languages?save=ok')

    security.declareProtected(view_management_screens, 'manage_delLanguages')
    def manage_delLanguages(self, languages, REQUEST=None):
        """
        Delete one or more languages.
        """
        self.getSite().gl_del_site_languages(languages)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_languages?save=ok')

    security.declareProtected(view_management_screens,
                              'manage_changeDefaultLang')
    def manage_changeDefaultLang(self, language, REQUEST=None):
        """
        Change the default portal language.
        """
        self.getSite().gl_change_site_defaultlang(language)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_languages?save=ok')

    #### Export Tab ####

    security.declareProtected(view_management_screens, 'manage_export')
    manage_export = PageTemplateFile('zpt/export_form', globals())

    security.declareProtected(view_management_screens, 'manage_export_po')
    def manage_export_po(self, language, REQUEST, RESPONSE):
        """ Provides pot/po export file for download """
        export_tool = self.get_importexport_tool()
        if language == 'locale.pot':
            filename = language
        else:
            filename = '%s.po' % language
        RESPONSE.setHeader('Content-type','application/data')
        RESPONSE.setHeader('Content-Disposition',
                           'inline;filename=%s' % filename)
        return export_tool.export_po(language)

    security.declareProtected(view_management_screens, 'manage_export_xliff')
    def manage_export_xliff(self, export_all, language, REQUEST, RESPONSE):
        """ Provides xliff file for download """
        fname = ('%s_%s.xlf'
                 % (self.get_message_catalog()._default_language, language))
        # Generate the XLIFF file header
        RESPONSE.setHeader('Content-Type', 'text/xml; charset=UTF-8')
        RESPONSE.setHeader('Content-Disposition',
                           'attachment; filename="%s"' % fname)
        export_tool = self.get_importexport_tool()
        return export_tool.export_xliff(language,
                                        export_all=bool(int(export_all)))

    security.declareProtected(view_management_screens, 'manage_export_tmx')
    def manage_export_tmx(self, REQUEST, RESPONSE):
        """ Provides tmx file for download """
        cat = self.get_message_catalog()
        fname = '%s.tmx' % cat.title
        export_tool = self.get_importexport_tool()
        header = export_tool.get_po_header(cat._default_language)
        charset = header['charset']
        # Generate the XLIFF file header
        RESPONSE.setHeader('Content-Type', 'text/xml; charset=%s' % charset)
        RESPONSE.setHeader('Content-Disposition',
                           'attachment; filename="%s"' % fname)
        return export_tool.export_tmx()

    #### Import Tab ####

    security.declareProtected(view_management_screens, 'manage_import')
    manage_import = PageTemplateFile('zpt/import_form', globals())

    security.declareProtected(view_management_screens, 'manage_import_po')
    def manage_import_po(self, file, language, REQUEST, RESPONSE):
        """ Import PO file into catalog, for an existing language """
        if language not in self.get_portal_lang_manager().getAvailableLanguages():
            raise ValueError('%s language is not available in portal' % language)
        else:
            import_tool = self.get_importexport_tool()
            import_tool.import_po(language, file)
        RESPONSE.redirect('manage_import?save=ok')

    security.declareProtected(view_management_screens, 'manage_import_tmx')
    def manage_import_tmx(self, file, language, REQUEST, RESPONSE):
        raise NotImplementedError("Tmx import is not yet implemented")

    security.declareProtected(view_management_screens, 'manage_import_xliff')
    def manage_import_xliff(self, file, language, REQUEST, RESPONSE):
        raise NotImplementedError("Xliff import is not yet implemented")
