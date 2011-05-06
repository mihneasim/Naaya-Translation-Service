# Python imports

# Zope imports
from zope.i18n.interfaces import ITranslationDomain
from zope.schema import TextLine
from zope.interface import implements
from zope.component import queryUtility
from Persistence import Persistent
from App.ImageFile import ImageFile
from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from zope.i18n import interpolate

# Naaya imports
from constants import ID_NAAYAI18N, TITLE_NAAYAI18N, METATYPE_NAAYAI18N

# Product imports
from LocalizerWrapper import LocalizerWrapper
from LanguageManagers import (NyPortalLanguageManager, NyLanguages)
from NyNegotiator import NyNegotiator
from NyMessageCatalog import LocalizerMessageCatalog
from interfaces import INyTranslationCatalog

def manage_addNaayaI18n(self, languages=('en', ), REQUEST=None, RESPONSE=None):
    """
    Add a new NaayaI18n instance (portal_i18n)
    """
    self._setObject(ID_NAAYAI18N, NaayaI18n(TITLE_NAAYAI18N, languages))

    if REQUEST is not None:
        RESPONSE.redirect('manage_main')

class NaayaI18n(Persistent, Folder):

    meta_type = METATYPE_NAAYAI18N
    #icon = 'misc_/icon.gif'

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    def __init__(self, title, languages=('en', )):
        self.title = title
        self._portal_langs = NyPortalLanguageManager(languages)
        self._catalog = INyTranslationCatalog(
                           LocalizerMessageCatalog('translation_catalog',
                                                   'Translation Catalog',
                                                   languages))

    def get_negotiator(self):
        if not hasattr(self, 'negotiator'):
            self.negotiator = NyNegotiator()
        return self.negotiator

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

    def get_selected_language(self, context=None):
        return self.get_negotiator().getLanguage(
                            self._portal_langs.getAvailableLanguages(), context)

    def add_language(self, lang):
        # add language to portal:
        self._portal_langs.addAvailableLanguage(lang)
        # and to catalog:
        self._catalog.add_language(lang)

    def del_language(self, lang):
        self._portal_langs.delAvailableLanguage(lang)
        self._catalog.del_language(lang)

    def changeLanguage(self, lang, goto=None, expires=None):
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

class NyLocalizerTranslator(object):

    implements(ITranslationDomain)

    def translate(self, msgid, mapping=None, context=None, target_language=None,
                  default=None):
        try:
            site = context['PARENTS'][0].getSite()
            localizer = LocalizerWrapper(site)
        except KeyError, e:
            # malformed Request, probably we are in a mock/testing env.
            return msgid

        # TODO: set target_language if we want to move negotiation here
        return localizer.translate(msgid, mapping, context, target_language,
                                   default)

class NyI18nTranslator(object):

    implements(ITranslationDomain)

    def translate(self, msgid, mapping=None, context=None, target_language=None,
                  default=None):
        try:
            site = context['PARENTS'][0].getSite()
        except KeyError, e:
            # malformed Request, probably we are in a mock/testing env.
            return msgid
        tool = site.getPortalI18n()
        if target_language is None:
            available = tool.get_portal_lang_manager().getAvailableLanguages()
            target_language = tool.get_negotiator().getLanguage(available,
                                                                context)
        if default is not None:
            raw = tool.get_catalog().gettext(msgid, target_language,
                                             default=default)
        else:
            raw = tool.get_catalog().gettext(msgid, target_language)
        return interpolate(raw, mapping)

def initialize(context):
    """ """

    context.registerClass(
        NaayaI18N,
        constructors = (manage_addNaayaI18N, ),
        icon='www/icon.gif')

InitializeClass(NaayaI18n)

misc_ = {
    'icon.gif': ImageFile('www/icon.gif', globals())
}
