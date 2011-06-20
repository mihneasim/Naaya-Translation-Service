
# Python imports
import logging
logger = logging.getLogger(__name__)

# Zope imports
import zope.thread
from zope.component import adapts
from zope.publisher.interfaces import IRequest
from ZPublisher.BaseRequest import DefaultPublishTraverse

# Naaya imports
from Products.Naaya.interfaces import INySite

class NySitePublishTraverse(DefaultPublishTraverse):
    adapts(INySite, IRequest)


    def publishTraverse(self, request, name):
        """
        There are 2 patches made on publish:
        * setting Request thread local and adding some i18n-related attributes
        on it. Useful for i18n operations when OFS context is unavailable.
        * hook for changing language by entering its code in url, after INySite

        """
        portal = self.context
        portal_i18n = portal.getPortalI18n()
        lang_manager = portal_i18n.get_portal_lang_manager()

        # set Request on thread.local and append i18n info on it
        patch_request(portal)
        if portal_i18n is not None:
            if name in lang_manager.getAvailableLanguages():
                request[portal_i18n.get_negotiator().cookie_id] = name
                # update selected language, it may be the one found in url
                request.i18n['selected_language'] = portal_i18n.get_selected_language()
                return portal
        return super(NySitePublishTraverse, self).publishTraverse(request, name)

def patch_request(portal):
    '''
     * Append i18n info required on request, when OFS context is unavailable
     * Put request on thread.local

    '''
    portal_i18n = portal.getPortalI18n()
    request = portal.REQUEST
    lang_manager = portal_i18n.get_portal_lang_manager()
    request.i18n = {}
    request.i18n['default_language'] = lang_manager.get_default_language()
    request.i18n['languages_mapping'] = portal_i18n.get_languages_mapping()
    request.i18n['selected_language'] = portal_i18n.get_selected_language()
    setRequest(request)

class NySiteInfo(zope.thread.local):
    #request = None
    pass

nysiteinfo = NySiteInfo()

def setRequest(request):
    nysiteinfo.request = request

def getRequest():
    return nysiteinfo.request
