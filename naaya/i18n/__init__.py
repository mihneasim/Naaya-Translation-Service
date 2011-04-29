# Python imports

# Zope imports
from zope.i18n.interfaces import ITranslationDomain
from zope.schema import TextLine
from zope.interface import implements
from zope.component import queryUtility

# Product imports
from LocalizerWrapper import LocalizerWrapper


class NyLocalizerTranslator(object):

    implements(ITranslationDomain)

    def translate(self, msgid, mapping=None, context=None, target_language=None,
                  default=None):
        try:
            site = context['PARENTS'][0].getSite()
            localizer = LocalizerWrapper(site)
        except KeyError, e:
            # malformed Request, probably we are in a mock/testing env.
            return msgid

        return localizer.translate(msgid, mapping, context, target_language,
                                   default)
