
# Zope imports
from zope.interface import implements

# Product imports
from Products.MyTranslationService.interfaces import ITranslationCatalog


class LocalizerWrapper(object):
    implements(ITranslationCatalog)
    
    def __init__(self, portal):
        self.cat = portal.getPortalTranslations()

    def edit_message(self, msgid, lang, translation):
        """ """
        # language existance test not present in Localizer:
        if lang not in self.get_languages():
            return
        # Add-by-edit functionality not present in Localizer:
        if not self.cat.message_exists(msgid):
            self.cat.gettext(msgid, lang, add=1)
        
        self.cat.message_edit(msgid, lang, translation,
                              note="Note not present in ITranslationCatalog api")

    def del_message(self, msgid):
        """ """
        self.cat.message_del(msgid)

    def gettext(self, msgid, lang, default=None):
        """Returns the corresponding translation of msgid in Catalog."""
        # language existance test not present in Localizer:
        if lang not in self.get_languages():
            add = 0
        else:
            add = 1
        return self.cat.gettext(msgid, lang, add=add, default=default)

    def get_languages(self):
        """Get available languages"""
        return self.cat.get_all_languages() # actually inherited from
        # LanguageManager, which returns get_languages(), inh. from Multilingual
        
    
    def add_language(self, lang):
        """Add language"""
        self.cat.manage_addLanguage(lang) # same comment as in get_languages
    
    def del_language(self, lang):
        """Delete language with corresponding messages"""
        self.cat.del_language(lang) # inh. from LanguageManager, inh.
        # from Multilingual. LanguageManager only has a manage_ method
        # which requires REQUEST and RESPONSE

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
