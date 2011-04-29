# -*- coding: UTF-8 -*-
# Python imports
import unittest

# Zope imports
from zope.i18n.interfaces import IModifiableUserPreferredLanguages

# Naaya imports
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase

# Project imports
from naaya.i18n.LanguageManagers import (NyLanguageManager,
                                         NyBrowserLanguageManager,
                                         NyPortalLanguageManager)


class LanguageManagersTest(unittest.TestCase):

    def test_language_manager_init(self):
        lang_manager = NyLanguageManager()
        # test languages.txt was used (we have some langs)
        self.assertTrue(len(lang_manager.langs) > 10)
        self.assertTrue(len(lang_manager.languages) > 10)

    def test_language_manager_add(self):
        lang_manager = NyLanguageManager()
        count0 = len(lang_manager.langs)
        lang_manager.add_language('en-pt', 'Pirate English')
        self.assertEqual(lang_manager.get_language_name('en-pt'),
                         'Pirate English')
        self.assertEqual(len(lang_manager.langs), count0 + 1)
        self.assertEqual(lang_manager.get_language_name('en-pt'), 'One more')
        self.assertEqual(len(lang_manager.langs), count0 + 1)
        self.assertEqual(lang_manager.get_language_name('en-pt'),
                         'Pirate English')

    def test_language_manager_del(self):
        #continue here
        lang_manager = NyLanguageManager()
        count0 = len(lang_manager.langs)
        lang_manager.add_language('en-pt', 'Pirate English')
        self.assertEqual(lang_manager.get_language_name('en-pt'),
                         'Pirate English')
        self.assertEqual(len(lang_manager.langs), count0 + 1)
        self.assertEqual(lang_manager.get_language_name('en-pt'), 'One more')
        self.assertEqual(len(lang_manager.langs), count0 + 1)
        self.assertEqual(lang_manager.get_language_name('en-pt'),
                         'Pirate English')
    

    def test_set_user_preferred(self):
        self.user_langs.setPreferredLanguages(('fr', 'en'))
        self.assertEqual(self.user_langs.getPreferredLanguages, ('fr', 'en'))

    def test_add_portal_language(self):
        self.portal_langs.addAvailableLanguage('en')
        self.portal_langs.addAvailableLanguage('fr')
        self.assertTrue('en' in self.portal_langs.getAvailableLanguages())
        self.assertTrue('fr' in self.portal_langs.getAvailableLanguages())

    def test_del_portal_language(self):
        self.portal_langs.addAvailableLanguage('fr')
        self.assertTrue('fr' in self.portal_langs.getAvailableLanguages())
        self.portal_langs.delAvailableLanguage('fr')
        self.assertFalse('fr' in self.portal_langs.getAvailableLanguages())
        def delete_all():
            for lang in self.portal_langs.getAvailableLanguages():
                self.portal_langs.delAvailableLanguage(lang)
        self.assertRaises(ValueError, delete_all)
