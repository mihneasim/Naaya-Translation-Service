
# Python imports
from lxml.html.soupparser import fromstring
from lxml.cssselect import CSSSelector
import re

# Zope imports
import transaction
from zope.app.component.site import threadSiteSubscriber

# Naaya imports
from Products.NaayaBase.NyContentType import NyContentData
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

# Product imports
from naaya.i18n.LocalPropertyManager import LocalAttribute


class LocalPropertyManagerTestSuite(NaayaFunctionalTestCase):

    def assertAttrValue(self, name, localized_value, effective_value):
        self.assertEqual(self.ob.getLocalProperty(name), localized_value)
        atr = getattr(self.ob, name)
        self.assertEqual(getattr(self.ob, name), effective_value)


    def setUp(self):
        super(LocalPropertyManagerTestSuite, self).setUp()
        self.ob = self.portal.info.accessibility

    def test_inexistent(self):
        self.assertRaises(AttributeError, self.assertAttrValue,
                          'inexistent', '', '')

    def test_not_localized(self):
        setattr(self.ob, 'an_attr', True)
        self.assertAttrValue('an_attr', '', True)

    def test_localized(self):
        self.ob._setLocalPropValue('specific', 'en', 'English')
        self.assertAttrValue('specific', 'English', 'English')

    def test_alsolocalized(self):
        self.ob._setLocalPropValue('title', 'en', 'English Title')
        self.assertAttrValue('title', 'English Title', 'English Title')
        setattr(self.ob, 'title', 'title attr')
        self.assertAttrValue('title', 'English Title', 'title attr')

        self.ob._setLocalPropValue('unspecific', 'en', 'English')
        setattr(self.ob, 'unspecific', 'unlocalized_value')
        self.assertAttrValue('unspecific', 'English', 'unlocalized_value')


class LocalPropertiesFunctionalTestSuite(NaayaFunctionalTestCase):

    def assertTitle(self, url_lang_sufix, value):
        #title = lambda x: x.xpath('//span[@class="page_title"]')[0].text or ''
        title = lambda x: CSSSelector("span.page_title")(x)[0].text_content()
        url = 'http://localhost/portal/'
        self.browser.go(url + url_lang_sufix)
        doc = fromstring(re.sub(r'\s+', ' ', self.browser.get_html()))
        self.assertEqual(title(doc), value)

    def setUp(self):
        super(LocalPropertiesFunctionalTestSuite, self).setUp()
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/portal_i18n/manage_languages')
        form = self.browser.get_form('manage_addLanguage')
        form['language_name'] = 'French'
        form['language_code'] = 'fr'
        self.browser.clicked(form,
                             self.browser.get_form_field(form, 'language_code'))
        self.browser.submit()
        self.portal.del_localproperty('site_title')
        transaction.commit()

    def test_with_both_translations(self):
        self.portal.set_localproperty('site_title', 'string', 'en', 'En title')
        self.portal.set_localproperty('site_title', 'string', 'fr', 'Fr titre')
        transaction.commit()
        # Tests:
        self.assertTitle('', 'En title')
        self.assertTitle('en', 'En title')
        self.assertTitle('fr', 'Fr titre')

    def test_without_translations(self):
        # Tests:
        self.assertTitle('', '')
        self.assertTitle('fr', '')

    def test_without_default_translation(self):
        self.portal.set_localproperty('site_title', 'string', 'fr', 'Fr titre')
        transaction.commit()
        # Tests:
        self.assertTitle('', '')
        self.assertTitle('fr', 'Fr titre')

    def test_without_secondary_translation(self):
        self.portal.set_localproperty('site_title', 'string', 'en', 'En title')
        transaction.commit()
        # Tests:
        self.assertTitle('', 'En title')
        self.assertTitle('fr', 'En title')
