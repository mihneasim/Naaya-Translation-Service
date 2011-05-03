
# Zope imports
from zope.i18n.interfaces import INegotiator, ILanguageAvailability
from zope.component import providedBy

# Naaya imports
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.constants import DEFAULT_PORTAL_LANGUAGE_CODE

# Product imports
from naaya.i18n.constants import (ID_NAAYAI18N, TITLE_NAAYAI18N,
                                  METATYPE_NAAYAI18N)
from naaya.i18n.interfaces import INyTranslationCatalog

class TestPortalTool(NaayaTestCase):

    def setUp(self):
        self.tool = getattr(self.portal, ID_NAAYAI18N, None)

    def test_existance(self):
        self.assertTrue(self.tool is not None)
        self.assertEqual(self.tool, self.portal.getPortalI18n())
        self.assertEqual(self.tool.title, TITLE_NAAYAI18N)
        self.assertEqual(self.tool.meta_type, METATYPE_NAAYAI18N)

    def test_components_attached(self):
        self.assertTrue(ILanguageAvailability.providedBy(self.tool.portal_manager))
        self.assertTrue(INegotiator.providedBy(self.tool.negotiator))
        self.assertTrue(INyTranslationCatalog.providedBy(self.tool.catalog))

class TestNySiteApi(NaayaTestCase):

    def setUp(self):
        self.portal.gl_add_site_language('de')

    def test_get_all_languages(self):
        known_langs = self.portal.gl_get_all_languages()
        self.assertTrue(isinstance(known_langs, list))
        self.assertTrue(len(known_langs) > 20) # length of languages.txt
        self.assertTrue(isinstance(known_langs[0], dict))
        self.assertTrue(known_langs[0].has_key('code'))
        self.assertTrue(known_langs[0].has_key('name'))
        # test sorted by code
        for i in range(len(known_langs)-1):
            self.assertTrue(known_langs[i]['code'] <= known_langs[i+1]['code'])

    def test_get_languages(self):
        self.assertEqual(self.portal.gl_get_languages(),
                         (DEFAULT_PORTAL_LANGUAGE_CODE, 'de'))

    def test_get_languages_mapping(self):
        mapping = self.portal.gl_get_languages_mapping()
        self.assertEqual(len(mapping), 2)
        self.assertTrue('de' in [x['code'] for x in mapping])
        self.assertTrue('en' in [x['code'] for x in mapping])
        self.assertEqual(['en'], [x['code'] for x in mapping if x['default']])

    def test_default_language(self):
        self.assertEqual(self.portal.gl_get_default_language(), 'en')
        self.portal.gl_change_site_defaultlang('de')
        self.assertEqual(self.portal.gl_get_default_language(), 'de')

    def test_get_selected_language(self):
        self.portal.REQUEST['TraversalRequestNameStack'].append('de')
        self.assertEqual(self.portal.gl_get_selected_language(), 'de')

    def test_get_languages_map(self):
        self.portal.REQUEST['TraversalRequestNameStack'].append('de')
        l_map = self.portal.gl_get_languages_map()
        self.assertEqual(len(l_map), 2)
        self.assertTrue('de' in [x['code'] for x in l_map])
        self.assertTrue('en' in [x['code'] for x in l_map])
        self.assertEqual(['de'], [x['code'] for x in map if x['selected']])

    def test_get_language_name(self):
        self.assertEqual(self.portal.gl_get_language_name('en-us'),
                         'English/United States')
        self.assertEqual(self.portal.gl_get_language_name('un-known'), '???')

    def test(self):
        pass
