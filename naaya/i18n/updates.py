from Products.naayaUpdater.updates import UpdateScript
from naaya.i18n.LocalizerWrapper import (register_adapted_localizer,
                                         TranslationDomainAdapter)
from zope.i18n.interfaces import ITranslationDomain
from zope.component import queryUtility

class RegisterTranslationUtilities(UpdateScript):
    title = 'Register Translation utilities in local site manager'
    creation_date = 'Apr 20, 2011'
    authors = ['Mihnea Simian']
    description = ('Register LocalizerWrapper utilities in local site manager')

    def _update(self, portal):
        ut = queryUtility(ITranslationDomain, 'default', context=portal)
        do_register = True
        if ut is not None:
            if isinstance(ut, TranslationDomainAdapter):
                self.log.debug('LocalizerWrapper already registered as'
                               ' ITranslationDomain provider')
                do_register = False
            else:
                self.log.debug('Unregistering existing utility %r' % ut)
                portal.getSiteManager().unregisterUtility(ut, ITranslationDomain,
                                                          'default')
        if do_register:
            register_adapted_localizer(portal)
            self.log.debug('ITranslationDomain(LocalizerWrapper) registered')
        return True
