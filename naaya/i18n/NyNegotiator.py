from zope.i18n.interfaces import INegotiator
from zope.interface import implements
from Persistence import Persistent

class NyNegotiator(Persistent):
    implements(INegotiator)

    def __init__(self, cookie_id='LOCALIZER_LANGUAGE', policy='browser'):    
        """
            * `cookie_id` is a key looked up in cookies/querystrings
            * `policy` can be browser, url, path, cookie, or any combination
            set as 'url --> path --> browser', default 'browser'
        """
        self.cookie_id = cookie_id
        self.policy = policy

    def _get_cache_key(self, available, client_langs):
        return self.policy + '/' + available + '/' + repr(client_langs)

    def _update_cache(self, cache_key, lang, request):
        if not request.has_key(self.cookie_id + '_cache'):
            request[self.cookie_id + '_cache'] = {}
        request[self.cookie_id + '_cache'][cache_key] = lang

    def _query_cache(self, cache_key, request):
        if (request.has_key(self.cookie_id + '_cache') and
            request[self.cookie_id + '_cache'].has_key(cache_key) and
            request[self.cookie_id + '_cache'][cache_key]):
            return request[self.cookie_id + '_cache'][cache_key]
        else:
            return None

    def getLanguage(self, available, request):
        """Returns the language dependent on the policy."""
        policy_list = self._policy.split(' --> ')
        AcceptLanguage = ''
        try:
            AcceptLanguage = REQUEST['AcceptLanguage']
        except KeyError:
            pass
        cookie = request.cookies.get(self.cookie_id, '')
        url = request.form.get(self.cookie_id)
        stack = request['TraversalRequestNameStack']
        # TODO: Shouldn't we check this is a language code?
        if stack:
            path = stack[-1]
        else:
            path = ''

        client_langs = {'browser': AcceptLanguage,
                        'url': url,
                        'path': path,
                        'cookie': cookie}

        # compute place in cache and check cache
        key = self._get_cache_key(available, client_langs)
        cached_value = self._query_cache(key, request)
        # 2nd assertion: one last check, just to make sure it's valid
        if cached_value is not None and cached_value in available:
            return cached_value

        for policy in policy_list:
            lang = client_langs[policy]
            if lang in available:
                self._update_cache(key, lang, request)
                return lang
        return available[0]
