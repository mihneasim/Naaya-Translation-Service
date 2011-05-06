# Python imports
import os.path
import re

# Zope imports
from zope.interface import implements
from zope.i18n.interfaces import (IModifiableUserPreferredLanguages,
                                  ILanguageAvailability)
from Persistence import Persistent

# Project imports
from interfaces import INyLanguageManagement


def normalize_code(code):
    not_letter = re.compile(r'[^a-z]+')
    return re.sub(not_letter, '-', code.lower())

class NyLanguages(object):

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
                self.languages[normalize_code(code)] = name

        # Builds a sorted list with the languages code and name
        language_codes = self.languages.keys()
        language_codes.sort()
        self.langs = [ {'code': x,
                        'name': self.languages[x]} for x in language_codes ]

    def add_language(self, code, name):
        """
        Returns code of added language, None if code already exists
        """
        code = normalize_code(code)
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
        code = normalize_code(code)
        if code not in self.languages.keys():
            raise KeyError("`%s` language code doesn't exist" % code)
        name = self.languages[code]
        del self.languages[code]
        self.langs.pop(self.langs.index({'code': code, 'name': name}))

    def get_language_name(self, code):
        """
        Returns the name of a language.
        """
        code = normalize_code(code)
        return self.languages.get(code, '???')

    def get_all_languages(self):
        return self.langs

class NyPortalLanguageManager(Persistent):

    implements(ILanguageAvailability)

    def __init__(self, default_langs=('en', )):
        if isinstance(default_langs, (str, unicode)):
            default_langs = (default_langs, )
        else:
            default_langs = tuple(default_langs)

        self.portal_languages = default_langs

    def getAvailableLanguages(self):
        """Return a sequence of language tags for available languages
        """
        return self.portal_languages

    def addAvailableLanguage(self, lang):
        """Adds available language in portal"""
        lang = normalize_code(lang)
        if lang not in self.portal_languages:
            self.portal_languages += (lang, )

    def delAvailableLanguage(self, lang):
        lang = normalize_code(lang)
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
        lang = normalize_code(lang)
        if lang not in self.portal_languages:
            raise ValueError("Language %s is not provided by portal" % lang)
        lst = list(self.portal_languages)
        if len(lst)==1:
            return
        lst.pop(lst.index(lang))
        lst.insert(0, lang)
        self.portal_languages = tuple(lst)

    def get_default_language(self):
        return self.portal_languages[0]
