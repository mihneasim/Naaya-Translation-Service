
# Zope imports
from zope.interface import implements
from zope.i18n.interfaces import ITranslationDomain
from zope.i18n import interpolate
from zope.component import adapts

# Product imports
from Products.MyTranslationService.interfaces import ITranslationCatalog
from Negotiator import negotiate


class LocalizerWrapper(object):
    implements(ITranslationCatalog)

    def __init__(self, portal):
        self.cat = portal.getPortalTranslations()

    def edit_message(self, msgid, lang, translation):
        """ """
        # language existance test **not present in Localizer**:
        if lang not in self.get_languages():
            return
        # Add-by-edit functionality **not present in Localizer**:
        if not self.cat.message_exists(msgid):
            self.cat.gettext(msgid, lang, add=1)

        self.cat.message_edit(msgid, lang, translation,
                              note="Note not present in ITranslationCatalog api")

    def del_message(self, msgid):
        """ """
        self.cat.message_del(msgid)

    def gettext(self, msgid, lang, default=None):
        """Returns the corresponding translation of msgid in Catalog."""
        # language existance test **not present in Localizer**:
        if lang not in self.get_languages():
            add = 0
        else:
            add = 1
        try:
            return self.cat.gettext(msgid, lang, add=add, default=default)
        except KeyError:
            # when add = 0 and msgid not in catalog
            return default or msgid

    def get_languages(self):
        """Get available languages"""
        return self.cat.get_languages() # actually inherited from
        # LanguageManager, where inherited from Multilingual

    def add_language(self, lang):
        """Add language"""
        self.cat.manage_addLanguage(lang) # same comment as in get_languages

    def del_language(self, lang):
        """Delete language with corresponding messages"""
        self.cat.del_language(lang) # inh. from LanguageManager, inh.
        # from Multilingual. LanguageManager only has a manage_ method
        # which requires REQUEST and RESPONSE

        # lang deletion also removes translations **not present in Localizer**
        for msgid in self.cat._messages.keys():
            if self.cat._messages[msgid].has_key(lang):
                del self.cat._messages[msgid][lang]

    def clear(self):
        """Erase all messages"""
        for msgid in self.cat._messages.keys():
            self.del_message(msgid)

    def messages(self):
        """
        Returns a generator used for catalog entries iteration.
        """
        for msgid in self.cat._messages.keys():
            yield msgid

class TranslationDomainAdapter(object):
    """ Using ITranslationCatalog, provides ITranslationDomain (zope.i18n) """

    def __init__(self, context):
        self.context = context

    def translate(self, msgid, mapping=None, context=None, target_language=None,
                  default=None):
        """
        * `context` is used in negotiaton - IUserPreferredLanguages(context)
        * `mapping` requires interpolation process
        """
        # gettext(msgid, lang, default=None)
        if target_language is None:
            target_language = negotiate(self.context.get_languages(), context)
        text = self.context.gettext(msgid, target_language, default)
        return interpolate(text, mapping)

def register_adapted_localizer(portal, domain='default'):
    """ Factory for ITranslationCatalog as ITranslationDomain;
        Needs to be registered with local site manager (depends on portal)
    """
    localizer = LocalizerWrapper(portal)
    lsm = portal.getSiteManager()
    lsm.registerUtility(ITranslationDomain(localizer), ITranslationDomain,
                        domain)
