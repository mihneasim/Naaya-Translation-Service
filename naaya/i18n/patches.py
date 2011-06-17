
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
        portal = self.context
        #print "Publish traverse:" + request['PATH_TRANSLATED']
        setNySite(portal)
        i18n_tool = portal.getPortalI18n()
        if i18n_tool is not None:
            lang_manager = i18n_tool.get_portal_lang_manager()
            if name in lang_manager.getAvailableLanguages():
                request[i18n_tool.get_negotiator().cookie_id] = name
                return portal
        return super(NySitePublishTraverse, self).publishTraverse(request, name)

class NySiteInfo(zope.thread.local):
    nysite = None

nysiteinfo = NySiteInfo()

def setNySite(nysite_ob):
    nysiteinfo.nysite = nysite_ob

def getNySite():
    return nysiteinfo.nysite
