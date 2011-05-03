
# Zope imports
from zope.i18n.interfaces import INegotiator
from zope.interface import implements
from Persistence import Persistent

# Product imports
from LanguageManagers import normalize_code

class NyNegotiator(Persistent):
    implements(INegotiator)

    def __init__(self, cookie_id='LOCALIZER_LANGUAGE', policy='browser'):    
        """
            * `cookie_id` is a key looked up in cookies/querystrings
            * `policy` can be 'browser', 'url', 'path', 'cookie',
            or any combination as a list of priorities
        """
        self.cookie_id = cookie_id
        self.set_policy(policy)

    def set_policy(self, policy):
        if isinstance(policy, str):
            policy = (policy, )
        else:
            policy = tuple(policy)
        for opt in policy:
            if opt not in ('browser', 'url', 'path', 'cookie'):
                raise ValueError('Invalid component for policy: "%s"' % opt)
        self.policy = policy

    def _get_cache_key(self, available, client_langs):
        return (','.join(self.policy) + '/' + ','.join(available) +
                '/' + repr(client_langs))

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

    # INegotiator interface:
    def getLanguage(self, available, request):
        """Returns the language dependent on the policy."""
        available = map(normalize_code, available)
        # here we keep {'xx': 'xx-zz'} for xx-zz, for fallback cases
        secondary = {}
        for x in [av for av in available if av.find("-") > -1]:
            secondary[x.split("-", 1)[0]] = x

        AcceptLanguage = ''
        try:
            AcceptLanguage = request['AcceptLanguage']
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

        client_langs = {'browser': normalize_code(AcceptLanguage),
                        'url': normalize_code(url),
                        'path': normalize_code(path),
                        'cookie': normalize_code(cookie)}

        # compute place in cache and check cache
        key = self._get_cache_key(available, client_langs)
        cached_value = self._query_cache(key, request)
        # 2nd assertion: one last check, just to make sure it's valid
        if cached_value is not None and cached_value in available:
            return cached_value

        for policy in self.policy:
            lang = client_langs[policy]
            if lang in available:
                self._update_cache(key, lang, request)
                return lang
            elif lang.find("-") > -1:
                first_code = lang.split("-", 1)[0]
                # if xx-yy not found, but xx is available, return xx
                if first_code in available:
                    return first_code
                # if xx-yy not found, but xx-zz is available, return xx-zz
                elif first_code in secondary.keys():
                    return secondary[first_code]

        return available[0]
