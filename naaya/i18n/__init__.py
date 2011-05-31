
# Zope imports
from zope.i18n.interfaces import ITranslationDomain
from zope.interface import implements
from zope.component import queryUtility, adapts
from App.ImageFile import ImageFile
from Globals import InitializeClass
from zope.i18n import interpolate
from zope.publisher.interfaces import IRequest
from ZPublisher.BaseRequest import DefaultPublishTraverse
from zope.app.component.interfaces import ISite

# Product imports
from portal_tool import NaayaI18n, manage_addNaayaI18n

try:
    from Products import Localizer
except ImportError:
    pass
else:
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

            # TODO: set target_language if we want to move negotiation here
            return localizer.translate(msgid, mapping, context, target_language,
                                       default)

class NySitePublishTraverse(DefaultPublishTraverse):
    adapts(ISite, IRequest)

    def fallback(self, request, name):
        sup = super(NySitePublishTraverse, self)
        return sup.publishTraverse(request, name)

    def publishTraverse(self, request, name):
        portal = request.PARENTS[-1]
        i18n_tool = portal.getPortalI18n()
        if (name and
            name in i18n_tool.get_portal_lang_manager().getAvailableLanguages()):
            request[i18n_tool.get_negotiator().cookie_id] = name
            return portal
        return self.fallback(request, name)


def traversalSubscriber(object, event):
    portal = object
    i18n_tool = portal.getPortalI18n()
    stack = portal.REQUEST['TraversalRequestNameStack']
    if (stack and
        (stack[-1] in i18n_tool.get_portal_lang_manager().getAvailableLanguages())):
        lang = stack.pop()
        portal.REQUEST[i18n_tool.get_negotiator] = lang

class NyI18nTranslator(object):

    implements(ITranslationDomain)

    def translate(self, msgid, mapping=None, context=None, target_language=None,
                  default=None):
        try:
            site = context['PARENTS'][0].getSite()
        except KeyError, e:
            # malformed Request, probably we are in a mock/testing env.
            return msgid
        tool = site.getPortalI18n()
        if target_language is None:
            available = tool.get_portal_lang_manager().getAvailableLanguages()
            target_language = tool.get_negotiator().getLanguage(available,
                                                                context)
        if default is not None:
            raw = tool.get_catalog().gettext(msgid, target_language,
                                             default=default)
        else:
            raw = tool.get_catalog().gettext(msgid, target_language)
        return interpolate(raw, mapping)

def initialize(context):
    """ """

    context.registerClass(
        NaayaI18n,
        constructors = (manage_addNaayaI18n, ),
        icon='www/icon.gif')

InitializeClass(NaayaI18n)

misc_ = {
    'icon.gif': ImageFile('www/icon.gif', globals())
}
