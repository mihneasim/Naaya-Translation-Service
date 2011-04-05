# Zope imports
from zope.interface import Interface

class ITranslationCatalog(Interface):
    
  
    def edit_message(msgid, lang, translation):
        """ """

    def del_message(msgid):
        """ """

    def gettext(msgid, lang, default=None):
        """Returns the corresponding translation of msgid in Catalog."""

    def get_languages():
        """Get available languages"""
    
    def add_language(lang):
        """Add language"""
    
    def del_language(lang):
        """Delete language with corresponding messages"""

    def clear():
        """Erase all messages"""

    def messages():
        """
        Returns a generator used for catalog entries iteration.
        """
