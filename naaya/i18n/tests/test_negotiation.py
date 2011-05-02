
from zope.i18n.interfaces import INegotiator
from zope.component import queryUtility

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase

class NegotiatorTestSuite(NaayaTestCase):

    cookie_id = 'LOCALIZER_LANGUAGE'

    def setUp(self):
        self.negotiator = queryUtility(INegotiator)
        self.req = self.portal.REQUEST
        self.req['AcceptLanguage'] = 'pt-br'
        self.req.cookies[self.cookie_id] = 'es'
        self.req['TraversalRequestNameStack'] = ['de', ]
        self.req.form[self.cookie_id] = 'fr'

    def test_normalize_code(self):
        sets = [('pt-br', 'pt-br'), ('en', 'en'), ('ro_RO', 'ro-ro'),
                ('PT BR', 'pt-br'), ('pt - br', 'pt-br'),
                ('sk-Cyrillic', 'sk-cyrillic')]
        for (input, expected) in sets:
            self.assertEqual(self.negotiator.normalize_code(input), expected)

    def test_negotiation_cache(self):
        client_langs = {'browser': 'pt-br',
                        'path': 'de',
                        'cookie': 'es',
                        'url': 'fr',
                        }
        self.negotiator.set_policy('browser --> path --> cookie --> url')

        key = self.negotiator._get_cache_key(('bg', 'fr'), client_langs)
        miss = self.negotiator._query_cache(key, self.req)
        self.assertEqual(miss, None)
        result = self.negotiator.getLanguage(('bg', 'fr'), self.req)
        self.assertEqual(result, 'fr')
        hit = self.negotiator._query_cache(key, self.req)
        self.assertEqual(hit, 'fr')

    def test_negotiate_url(self):
        self.negotiator.set_policy('url')
        result = self.negotiator.getLanguage(('en', 'de', 'fr'), self.req)
        self.assertEqual(result, 'fr')

    def test_negotiate_path(self):
        self.negotiator.set_policy('path')
        result = self.negotiator.getLanguage(('en', 'de', 'fr'), self.req)
        self.assertEqual(result, 'de')

    def test_negotiate_cookie(self):
        self.negotiator.set_policy('cookie')
        result = self.negotiator.getLanguage(('en', 'es', 'fr'), self.req)
        self.assertEqual(result, 'es')


    def test_negotiate_browser(self):
        self.negotiator.set_policy('browser')
        result = self.negotiator.getLanguage(('en', 'pt_BR', 'fr'), self.req)
        self.assertEqual(result, 'pt-br')

    def test_negotiate_partial(self):
        self.negotiator.set_policy('cookie')
        self.req.cookies[self.cookie_id] = 'pt-un'
        result = self.negotiator.getLanguage(('en', 'pt-br', 'pt-un', 'fr'), self.req)
        self.assertEqual(result, 'pt-un')
        result = self.negotiator.getLanguage(('en', 'pt-br', 'fr'), self.req)
        self.assertEqual(result, 'pt-br')
        result = self.negotiator.getLanguage(('en', 'pt', 'fr'), self.req)
        self.assertEqual(result, 'pt')

    def test_negotiate_priorities(self):
        self.negotiator.set_policy('cookie --> browser --> url')
        self.req.cookies[self.cookie_id] = 'bg' # fails
        self.req['AcceptLanguage'] = 'es' # fails
        self.req.form[self.cookie_id] = 'de' # hits
        result = self.negotiator.getLanguage(('en', 'de', 'fr'), self.req)
        self.assertEqual(result, 'de')

    def test_default_fallback(self):
        self.req.cookies[self.cookie_id] = 'fr' # fails
        result = self.negotiator.getLanguage(('de', 'en', 'es'), self.req)
        self.assertEqual(result, 'de')
