# -*- coding: UTF-8 -*-
# Python imports
import unittest
from mock import patch

# Zope imports
from zope.i18n.interfaces import IModifiableUserPreferredLanguages

# Naaya imports
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase

# Project imports
from Products.MyTranslationService.interfaces import ILanguageManagement
from Products.MyTranslationService.LocalizerWrapper import register_adapted_localizer


class LanguageManagersTest(NaayaTestCase):


    def setUp(self):
        register_adapted_localizer(self.portal)
        lsm = self.portal.getSiteManager()
        self.user_langs = lsm.queryUtility(IModifiableUserPreferredLanguages)
        self.portal_langs = lsm.queryUtility(ILanguageManagement)
        #import pdb; pdb.set_trace()

    def test_set_user_preferred(self):
        self.user_langs.setPreferredLanguages('fr', 'en')
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
