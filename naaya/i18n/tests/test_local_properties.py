
# Python imports
from lxml.html.soupparser import fromstring
import re

# Zope imports
import transaction

# Naaya imports
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

# Helper closures
title = lambda x: x.xpath('//span[@class="page_title"]')[0].text or ''
subtitle = lambda x: x.xpath('//span[@class="page_subtitle"]')[0].text or ''


class LocalPropertiesTestSuite(NaayaFunctionalTestCase):

    def afterSetUp(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/portal_i18n/manage_languages')
        form = self.browser.get_form('manage_addLanguage')
        form['language_name'] = 'French'
        form['language_code'] = 'fr'
        self.browser.clicked(form,
                             self.browser.get_form_field(form, 'language_code'))
        self.browser.submit()
        self.portal.del_localproperty('site_title')
        self.portal.del_localproperty('site_subtitle')
        transaction.commit()

    def test_with_both_translations(self):
        self.portal.set_localproperty('site_title', 'string', 'en', 'En title')
        self.portal.set_localproperty('site_subtitle', 'string', 'en', 'En subtitle')
        self.portal.set_localproperty('site_title', 'string', 'fr', 'Fr titre')
        self.portal.set_localproperty('site_subtitle', 'string', 'fr', 'Fr subtitre')
        transaction.commit()
        # Tests:
        self.browser.go('http://localhost/portal')
        doc = fromstring(re.sub(r'\s+', ' ', self.browser.get_html()))
        self.assertEqual(title(doc), 'En title')
        self.assertEqual(subtitle(doc), 'En subtitle')
        self.browser.go('http://localhost/portal/fr')
        doc = fromstring(re.sub(r'\s+', ' ', self.browser.get_html()))
        self.assertEqual(title(doc), 'Fr titre')
        self.assertEqual(subtitle(doc), 'Fr subtitre')

    def test_without_translations(self):
        # Tests:
        self.browser.go('http://localhost/portal')
        doc = fromstring(re.sub(r'\s+', ' ', self.browser.get_html()))
        self.assertEqual(title(doc), '')
        self.assertEqual(subtitle(doc), '')
        self.browser.go('http://localhost/portal/fr')
        doc = fromstring(re.sub(r'\s+', ' ', self.browser.get_html()))
        self.assertEqual(title(doc), '')
        self.assertEqual(subtitle(doc), '')

    def test_without_default_translation(self):
        self.portal.set_localproperty('site_title', 'string', 'fr', 'Fr titre')
        self.portal.set_localproperty('site_subtitle', 'string', 'fr', 'Fr subtitre')
        transaction.commit()
        # Tests:
        self.browser.go('http://localhost/portal')
        doc = fromstring(re.sub(r'\s+', ' ', self.browser.get_html()))
        self.assertEqual(title(doc), '')
        self.assertEqual(subtitle(doc), '')
        self.browser.go('http://localhost/portal/fr')
        doc = fromstring(re.sub(r'\s+', ' ', self.browser.get_html()))
        self.assertEqual(title(doc), 'Fr titre')
        self.assertEqual(subtitle(doc), 'Fr subtitre')

    def test_without_secondary_translation(self):
        self.portal.set_localproperty('site_title', 'string', 'en', 'En title')
        self.portal.set_localproperty('site_subtitle', 'string', 'en', 'En subtitle')
        transaction.commit()
        # Tests:
        self.browser.go('http://localhost/portal')
        doc = fromstring(re.sub(r'\s+', ' ', self.browser.get_html()))
        self.assertEqual(title(doc), 'En title')
        self.assertEqual(subtitle(doc), 'En subtitle')
        self.browser.go('http://localhost/portal/fr')
        doc = fromstring(re.sub(r'\s+', ' ', self.browser.get_html()))
        self.assertEqual(title(doc), 'En title')
        self.assertEqual(subtitle(doc), 'En subtitle')
