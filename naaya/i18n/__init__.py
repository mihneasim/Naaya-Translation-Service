# Python imports

# Zope imports
from zope.i18n.interfaces import ITranslationDomain
from zope.schema import TextLine
from zope.interface import implements
from zope.component import queryUtility

# Product imports
from Negotiator import negotiate

class TranslationService(object):

    # mocking
    available_languages = ('en', 'de', )

class Translator(TranslationService):

    implements(ITranslationDomain)

    def translate(self, msgid, mapping=None, context=None, target_language=None,
                  default=None):

        try:
            site = context['PARENTS'][0].getSite()
        except KeyError, e:
            # malformed Request, probably we are in a mock/testing env.
            return msgid

        ts = queryUtility(ITranslationDomain, 'default', context=site)
        return ts.translate(msgid, mapping, context, target_language, default)
