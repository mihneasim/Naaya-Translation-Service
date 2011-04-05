# Python imports
import unittest
from mock import patch

# Naaya imports
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase

# Project imports
from Products.MyTranslationService.interfaces import ITranslationCatalog
from Products.MyTranslationService.LocalizerWrapper import LocalizerWrapper


class TranslationCatalogTest(unittest.TestCase):
    
    catalog_factory = None # TBC
    
    def test_message_operations(self):
        catalog = self.catalog_factory(languages=('en', 'de'))

        self.assertRaises(StopIteration, catalog.messages().next)

        cat_en = catalog.gettext('cat', 'en')
        cat_de = catalog.gettext('cat', 'de')
        self.assertEqual((cat_en, cat_de), ('cat', 'cat'))

        catalog.edit_message('cat', 'en', 'cat')
        catalog.edit_message('cat', 'de', 'Katze')
        cat_de = catalog.gettext('cat', 'de')
        self.assertEqual(catalog.gettext('cat', 'de'), 'Katze')

        catalog.edit_message('water', 'en', 'water')
        catalog.edit_message('water', 'de', 'Wasser')
        catalog.del_message('cat')
        # cat is not present in catalog, but will be added in the first call
        self.assertEqual(catalog.gettext('cat', 'en'), None)
        # cat is now in catalog, but no translation, return msgid
        self.assertEqual(catalog.gettext('cat', 'en'), 'cat')
        # return default if given, since translation not available
        self.assertEqual(catalog.gettext('cat', 'en', 'default'), 'default')
        
        # test iteration, 'water' and 'cat' in catalog
        i = 0
        try:
            while True:
                catalog.messages().next()
                i += 1
        except StopIteration:
            pass
        self.assertEqual(i, 2)

    def test_language_operations(self):

        catalog = self.catalog_factory(languages=('en', 'de'))
        catalog.edit_message('dog', 'de', 'Hund')
        catalog.del_language('de')
        self.assertFalse('de' in catalog.get_languages())
        # since missing translation, but word in dict, must return msgid:
        self.assertEqual(catalog.gettext('dog', 'de'), 'dog')
        
        catalog.add_language('fr')
        self.assertTrue('fr' in catalog.get_languages())
        self.assertEqual(catalog.gettext('dog', 'fr'), 'dog')

class LocalizerAdapterTest(NaayaTestCase, TranslationCatalogTest):
    def catalog_factory(self, **kw):
        """ create, clean and return Localizer instance here"
