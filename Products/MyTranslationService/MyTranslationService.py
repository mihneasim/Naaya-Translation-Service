# Python imports

# Zope imports
from zope.i18n.interfaces import ITranslationDomain
from zope.schema import TextLine
from zope.interface import implements
from zope.component import queryUtility

# Product imports
from Negotiator import negotiate

class MyTranslationService(object):
    
    # mocking
    available_languages = ('en', 'de', )

class MyTranslator(MyTranslationService):
    
    implements(ITranslationDomain)

    def __init__(self):
        pass


    def translate(self, msgid, mapping=None, context=None, target_language=None,
                  default=None):

        lsm = context['PARENTS'][0].getSite().getSiteManager()
        ts = lsm.queryUtility(ITranslationDomain, 'default')
        return ts.translate(msgid, mapping, context, target_language, default)
        # OLD, TEST STUFF
        #lang = negotiate(self.available_languages, context)
        #return 'my-translation(%s)' % lang

    def __call__(self):
        pass
