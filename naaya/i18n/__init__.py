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

# Naaya imports
from constants import ID_NAAYAI18N, TITLE_NAAYAI18N, METATYPE_NAAYAI18N

# Product imports
from LocalizerWrapper import LocalizerWrapper
from LanguageManagers import (NyPortalLanguageManager, NyLanguages)
from NyNegotiator import NyNegotiator
from NyMessageCatalog import LocalizerMessageCatalog
from interfaces import INyTranslationCatalog

def manage_addNaayaI18N(self, languages=('en', ), REQUEST=None, RESPONSE=None):
    """
    Add a new NaayaI18N instance (portal_i18n)
    """
    self._setObject(ID_NAAYAI18N, NaayaI18N(TITLE_NAAYAI18N, languages))

    if REQUEST is not None:
        RESPONSE.redirect('manage_main')

class NaayaI18N(Persistent, Folder):

    meta_type = METATYPE_NAAYAI18N
    #icon = 'misc_/icon.gif'

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    def __init__(self, title, languages=('en', )):
        self.title = title
        self.portal_langs = NyPortalLanguageManager(languages)
        self.catalog = INyTranslationCatalog(
                           LocalizerMessageCatalog('translation_catalog',
                                                   'Translation Catalog',
                                                   languages))

    def get_negotiator(self):
        if not hasattr(self, 'negotiator'):
            self.negotiator = NyNegotiator()
        return self.negotiator

    def get_lang_manager(self):
        if not hasattr(self, 'lang_manager'):
            self.lang_manager = NyLanguages()
        return self.lang_manager

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
            available = tool.portal_langs.getAvailableLanguages()
            target_language = tool.get_negotiator().getLanguage(available,
                                                                context)
        if default is not None:
            return tool.catalog.gettext(msgid, target_language, default=default)
        else:
            return tool.catalog.gettext(msgid, target_language)

def initialize(context):
    """ """

    context.registerClass(
        NaayaI18N,
        constructors = (manage_addNaayaI18N, ),
        icon='www/icon.gif')

InitializeClass(NaayaI18N)

misc_ = {
    'icon.gif': ImageFile('www/icon.gif', globals())
}
