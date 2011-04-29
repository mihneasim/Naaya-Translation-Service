
from zope.i18n.interfaces import INegotiator
from zope.component import queryUtility
from Products.PageTemplates.PageTemplate import PageTemplate

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase

class TranslationsTest(NaayaTestCase):

    cookie_id = 'LOCALIZER_LANGUAGE'

    def setUp(self):
        self.negotiator = queryUtility(INegotiator)
        self.tmpl = PageTemplate(id='test_tmpl')
        self.tmpl.pt_edit('<p i18n:translate="">Home for'
                          ' <span i18n:name="hours">3</span> hours</p>')

    def test_template_translation(self):
        self.portal.REQUEST['AcceptLanguage'] = 'fr'
        self.portal.getNegotiator().policy = 'browser'
        self.assertEqual(self.tmpl.__of__(self.portal)(),
                         '<p>Home for <span>3</span> hours</p>')
        self.portal.getLocalizer().edit_message('Home for ${hours} hours', 'fr',
                                                'Au l\'accueil pendant ${hours} heures')
        self.assertEqual(self.tmpl.__of__(self.portal)(),
                         '<p>Au l\'accueil pendant <span>3</span> heures</p>')
