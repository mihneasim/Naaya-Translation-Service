
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

    def fallback(self, request, name):
        sup = super(NySitePublishTraverse, self)
        return sup.publishTraverse(request, name)

    def publishTraverse(self, request, name):
        portal = request.PARENTS[-1]
        print "Publish traverse:" + request['PATH_TRANSLATED']
        setNySite(portal)
        i18n_tool = portal.getPortalI18n()
        if (name and
            name in i18n_tool.get_portal_lang_manager().getAvailableLanguages()):
            request[i18n_tool.get_negotiator().cookie_id] = name
            return portal
        return self.fallback(request, name)

class NySiteInfo(zope.thread.local):
    nysite = None

nysiteinfo = NySiteInfo()

def setNySite(nysite_ob):
    nysiteinfo.nysite = nysite_ob

def getNySite():
    return nysiteinfo.nysite
