# Python imports
import os.path

# Zope imports
from zope.interface import implements
from zope.i18n.interfaces import (IModifiableUserPreferredLanguages,
                                  ILanguageAvailability)
from Persistence import Persistent

# Project imports
from interfaces import INyLanguageManagement


class NyLanguageManager(Persistent):

    def __init__(self):
        self.reset()

    def reset(self):
        self.languages = {}
        cwd = __file__.rsplit(os.path.sep, 1)[0]
        filename = os.path.join(cwd, 'languages.txt')
        for line in open(filename).readlines():
            line = line.strip()
            if line and line[0] != '#':
                code, name = line.split(' ', 1)
                self.languages[code] = name
        
        # Builds a sorted list with the languages code and name
        language_codes = self.languages.keys()
        language_codes.sort()
        self.langs = [ {'code': x,
                        'name': self.languages[x]} for x in language_codes ]

    def add_language(self, code, name):
        """
        Returns code of added language, None if code already exists
        """
        if self.languages.has_key(code):
            raise KeyError("`%s` language code already exists" % code)
        self.languages[code] = name
        language_codes = self.languages.keys()
        language_codes.sort()
        self.langs = [ {'code': x,
                        'name': self.languages[x]} for x in language_codes ]

    def del_language(self, code):
        """
        Returns deleted language code, None if language code not found
        """
        if code not in self.languages.keys():
            raise KeyError("`%s` language code doesn't exist" % code)
        name = self.languages[code]
        del self.languages[code]
        self.langs.pop(self.langs.index({'code': code, 'name': name}))

    def get_language_name(self, code):
        """
        Returns the name of a language.
        """
        return self.languages.get(code, '???')
    
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
            self.portal_languages += (lang, )

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
