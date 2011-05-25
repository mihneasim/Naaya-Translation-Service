# -*- coding: UTF-8 -*-
# Python imports
from time import time

# Zope
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from ExtensionClass import Base
from zope.app.component.hooks import getSite


class LocalAttribute(Base):
    """
    Provides a way to override class variables, useful for example
    for title (defined in SimpleItem).
    """

    def __init__(self, id):
        self.id = id

    def __of__(self, parent):
        return parent.getLocalAttribute(self.id)

# XXX
# For backwards compatibility
# (localizer <= 0.8.0): other classes import 'LocalProperty'
LocalProperty = LocalAttribute

class LocalPropertyManager(object):
    """
    Mixin class that allows to manage localized properties.
    Somewhat similar to OFS.PropertyManager.
    """

    security = ClassSecurityInfo()

    # Metadata for local properties
    # Example: ({'id': 'title', 'type': 'string'},)
    _local_properties_metadata = ()

    # Local properties are stored here
    # Example: {'title': {'en': ('Title', timestamp), 'es': ('Títul', timestamp)}}
    _local_properties = {}

    # Useful to find or index all LPM instances
    isLocalPropertyManager = 1

    security.declarePublic('hasLocalProperty')
    def hasLocalProperty(self, id):
        """Return true if object has a property 'id'"""
        for property in self._local_properties_metadata:
            if property['id'] == id:
                return 1
        return 0

    security.declareProtected('Manage properties', 'set_localpropvalue')
    def set_localpropvalue(self, id, lang, value):
        # Get previous value
        old_value = self.getLocalAttribute(id, lang)
        # Update value only if it is different
        if value != old_value:
            properties = self._local_properties.copy()
            if not properties.has_key(id):
                properties[id] = {}

            properties[id][lang] = (value, time())

            self._local_properties = properties

    #def get_localproperty(self, name, language):
    #    if name not in self._local_properties:
    #        return None, None
    #    property = self._local_properties[name]
    #    if language not in property:
    #        return None, None
    #    value = property[language]
    #    if isinstance(value, tuple):
    #        return value
    #    return value, None

    security.declareProtected('Manage properties', 'set_localproperty')
    def set_localproperty(self, id, type, lang=None, value=None):
        """Adds a new local property"""
        if not self.hasLocalProperty(id):
            self._local_properties_metadata += ({'id': id, 'type': type},)
            setattr(self, id, LocalProperty(id))

        if lang is not None:
            self.set_localpropvalue(id, lang, value)

    security.declareProtected('Manage properties', 'del_localproperty')
    def del_localproperty(self, id):
        """Deletes a property"""
        # Update properties metadata
        p = [ x for x in self._local_properties_metadata if x['id'] != id ]
        self._local_properties_metadata = tuple(p)

        # delete attribute
        try:
            del self._local_properties[id]
        except KeyError:
            pass

        try:
            delattr(self, id)
        except KeyError:
            pass

    # XXX Backwards compatibility
    _setLocalPropValue = set_localpropvalue
    _setLocalProperty = set_localproperty
    _delLocalProperty = del_localproperty

    security.declarePublic('getLocalProperties')
    def getLocalProperties(self):
        """Returns a copy of the properties metadata."""
        return tuple([ x.copy() for x in self._local_properties_metadata ])

    security.declarePublic('getLocalAttribute')
    def getLocalAttribute(self, id, lang=None):
        """Returns a local property"""
        if id not in self._local_properties:
            return ''
        # No language, look for the first non-empty available version
        if lang is None:
            i18n_tool = self.get_portal_i18n()
            #lang = i18n_tool.get_selected_language(property=id)
            # need to negotiate lang based on available langs for this prop.
            lang = i18n_tool.get_negotiator().\
                getLanguage(self._local_properties[id].keys())
        if lang not in self._local_properties[id]:
            return ''
        value = self._local_properties[id][lang]
        if isinstance(value, tuple): # (value, timestamp)
            return value[0]
        else:
            return value

    # XXX For backwards compatibility (<= 0.8.0)
    getLocalProperty = getLocalAttribute

    def __getattr__(self, name):
        try:
            index = name.rfind('_')
            id, lang = name[:index], name[index+1:]
            property = self._local_properties[id]
        except:
            raise AttributeError, "%s instance has no attribute '%s'" \
                                  % (self.__class__.__name__, name)

        return self.getLocalAttribute(id, lang)

    security.declarePublic('get_portal_i18n')
    def get_portal_i18n(self):
        """ """
        if getSite() is not None:
            # preferred, acquisiton may be overwritten, use hook before traversal
            return getSite().getPortalI18n()
        else:
            # no traversal, use acquisition
            return self.getSite().getPortalI18n()

    ### For compatibility with old property manager - for here/get_lang..
    security.declarePublic('get_languages_mapping')
    def get_languages_mapping(self):
        return self.get_portal_i18n().get_languages_mapping()

    security.declarePublic('get_language_name')
    def get_language_name(self, lang):
        return self.get_portal_i18n().get_language_name(lang)

InitializeClass(LocalPropertyManager)
