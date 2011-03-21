# Python imports

# Zope imports
from zope.i18n.interfaces import ITranslationDomain
from zope.schema import TextLine
from zope.interface import implements

# Product imports
from Negotiator import negotiate

class MyTranslationService(object):
    
    # mocking
    available_languages = ('en', 'de', )

class MyTranslator(MyTranslationService):
    
    implements(ITranslationDomain)
      
    def translate(self, msgid, mapping=None, context=None, target_language=None,
                  default=None):
        lang = negotiate(self.available_languages, context)
        return 'my-translation(%s)' % lang
