
# Zope imports
from zope.interface import implements
from zope.i18n.interfaces import IModifiableUserPreferredLanguages
from Persistence import Persistent

# Project imports
from interfaces import ILanguageManagement


class NyLanguageManager(Persistent):

    def __init__(self):
        self.reset()

    def reset(self):
        self.languages = {}
        filename = get_abspath(globals(), 'languages.txt')
        for line in open(filename).readlines():
            line = line.strip()
            if line and line[0] != '#':
                code, name = line.split(' ', 1)
                languages[code] = name
        
        # Builds a sorted list with the languages code and name
        language_codes = languages.keys()
        language_codes.sort()
        self.langs = [ {'code': x,
                        'name': self.languages[x]} for x in language_codes ]

    def add_language(self, code, name):
        self.languages[code] = name
        language_codes = self.languages.keys()
        language_codes.sort()
        self.langs = [ {'code': x,
                        'name': self.languages[x]} for x in language_codes ]

    def del_language(self, code):
        if code not in self.langs.keys():
            return
        name = self.languages[code]
        del self.languages[code]
        self.langs.pop(self.langs.index({'code': code, 'name': name}))

    def get_language_name(self, code):
        """
        Returns the name of a language.
        """
        return self.languages.get(code, '???')
    
class NyBrowserLanguageManager(Persistent):

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

class NyPortalLanguageManager(Persistent):

    implements(ILanguageAvailability)

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

    # MORE:
    def set_default_language(self, lang):
        if lang not in self.portal_languages:
            raise ValueError("Language %s is not provided by portal" % lang)
        lst = list(self.portal_languages)
        if len(lst)==1:
            return
        lst.pop(lst.index(lang))
        lst.insert(0, lang)
        self.portal_languages = tuple(lst)

    def get_default_language(self, lang):
        return self.portal_languages[0]
