
# Zope imports
from zope.interface import implements
from zope.i18n.interfaces import IModifiableUserPreferredLanguages

# Project imports
from interfaces import ILanguageManagement

class ClientLanguageManager(object):

    implements(IModifiableUserPreferredLanguages)
    # inherits IUserPreferredLanguages

    def __init__(self):
        self.client_languages = ('en', )

    def getPreferredLanguages(self):
        """Return a sequence of user preferred languages.

        The sequence is sorted in order of quality, with the most preferred
        languages first.
        """
        return self.client_languages

    def setPreferredLanguages(self, languages):
        """Set a sequence of user preferred languages.

        The sequence should be sorted in order of quality, with the most
        preferred languages first.
        """
        self.client_languages = tuple(languages)

class PortalLanguageManager(object):

    implements(ILanguageAvailability)
    # by inheritance, also ILanguageAvailability

    def __init__(self):
        self.portal_languages = ('en', )

    def getAvailableLanguages(self):
        """Return a sequence of language tags for available languages
        """
        return self.portal_languages

    def addAvailableLanguage(self, lang):
        """Adds available language in portal"""
        if lang not in self.portal_languages:
            self.portal_languages += lang

    def delAvailableLanguage(self, lang):
        new_list = []
        for av_lang in self.portal_languages:
            if av_lang != lang:
                new_list.append(av_lang)
        if len(new_list):
            self.portal_languages = tuple(new_list)
        else:
            raise ValueError("Can not delete the only available language")
