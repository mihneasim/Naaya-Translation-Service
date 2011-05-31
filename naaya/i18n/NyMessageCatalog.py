
# Python imports

# Zope imports
from Globals import PersistentMapping, InitializeClass
from OFS.SimpleItem import SimpleItem
from ZPublisher import HTTPRequest
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from zope.app.component.hooks import getSite

# itools
from itools.i18n.base import Multilingual

# Product imports
from interfaces import INyTranslationCatalog

# Do we still need this?
def update_transaction_note():
    import transaction, re

    def label_with_count(count):
        return "(Saving %d new localizer messages)" % count
    def increment_count(match):
        return label_with_count(int(match.group('count')) + 1)
    p = re.compile(r'\(Saving (?P<count>\d+) new localizer messages\)')

    t = transaction.get()
    if p.search(t.description) is None:
        t.note(label_with_count(0))
    t.description = p.sub(increment_count, t.description)


class LocalizerMessageCatalog(Multilingual, SimpleItem):
    """Stores messages and their translations...
    """

    meta_type = 'MessageCatalog'
    security = ClassSecurityInfo()

    def __init__(self, id, title, languages=('en', )):
        self.id = id

        self.title = title

        # Language Manager data
        self._languages = tuple(languages)
        self._default_language = self._languages[0]

        # Here the message translations are stored
        self._messages = PersistentMapping()

    #######################################################################
    # Private API
    #######################################################################
    def get_message_key(self, message):
        if message in self._messages:
            return message
        # A message may be stored as unicode or byte string
        encoding = HTTPRequest.default_encoding
        if isinstance(message, unicode):
            message = message.encode(encoding)
        else:
            message = unicode(message, encoding)
        if message in self._messages:
            return message

    def get_translations(self, message):
        message = self.get_message_key(message)
        return self._messages[message]


    #######################################################################
    # Public API
    #######################################################################
    def message_exists(self, message):
        """ """
        return self._messages.has_key(message)


    def message_edit(self, message, language, translation, note):
        """ """
        self._messages[message][language] = translation
        self._messages[message]['note'] = note

    def message_del(self, message):
        """ """
        del self._messages[message]

    security.declarePublic('gettext')
    def gettext(self, message, lang, add=1, default=None):
        """Returns the message translation from the database if available.

        If add=1, add any unknown message to the database.
        If a default is provided, use it instead of the message id
        as a translation for unknown messages.
        """
        if not isinstance(message, (str, unicode)):
            raise TypeError, 'only strings can be translated.'

        message = message.strip()
        # assume empty message is always translated as empty message
        if not message:
            return message

        if default is None:
            default = message

        # Add it if it's not in the dictionary
        if add and not self._messages.has_key(message) and message:
            # TODO: What is this?
            update_transaction_note()
            self._messages[message] = PersistentMapping()

        if message and not self._messages[message].has_key('en'):
            self._messages[message]['en'] = default

        # Get the string
        if self._messages.has_key(message):
            m = self._messages[message]
            return m.get(lang) or default

        return default

class NyMessageCatalogAdapter(SimpleItem):
    ''' adapter for the upwards class '''
    implements(INyTranslationCatalog)

    security = ClassSecurityInfo()

    def __init__(self, object):
        self.cat = object
        self._po_headers = {}

    ### INyTranslationCatalog

    def edit_message(self, msgid, lang, translation):
        """ """
        # language existance test **not present in Localizer**:
        if lang not in self.get_languages():
            return
        # Add-by-edit functionality **not present in Localizer**:
        if not self.cat.message_exists(msgid):
            self.cat.gettext(msgid, lang, add=1)

        self.cat.message_edit(msgid, lang, translation,
                              note="`Note` not present in INyTranslationCatalog")

    def del_message(self, msgid):
        """ """
        self.cat.message_del(msgid)

    security.declarePublic('gettext')
    def gettext(self, msgid, lang=None, default=None):
        """Returns the corresponding translation of msgid in Catalog."""

        # Fix language / rare - translation without ITranslationDomain utility!
        if lang is None:
            # hope for acquisition; localizer used to patch request
            lang = self.getPortalI18n().get_negotiator().getLanguage(
             self.getPortalI18n().get_portal_lang_manager().getAvailableLanguages()
            )

        # language existance test **not present in Localizer**:
        if lang not in self.get_languages():
            add = 0
        else:
            add = 1
        try:
            return self.cat.gettext(msgid, lang, add=add, default=default)
        except KeyError:
            # when add = 0 and msgid not in catalog
            return default or msgid

    def get_languages(self):
        """Get available languages"""
        return self.cat.get_languages() # actually inherited from
        # LanguageManager, where inherited from Multilingual

    def add_language(self, lang):
        """Add language"""
        self.cat.add_language(lang) # same comment as in get_languages

    def del_language(self, lang):
        """Delete language with corresponding messages"""
        self.cat.del_language(lang) # inh. from LanguageManager, inh.
        # from Multilingual. LanguageManager only has a manage_ method
        # which requires REQUEST and RESPONSE

        # lang deletion also removes translations **not present in Localizer**
        for msgid in self.cat._messages.keys():
            if self.cat._messages[msgid].has_key(lang):
                del self.cat._messages[msgid][lang]

    def clear(self):
        """Erase all messages"""
        for msgid in self.cat._messages.keys():
            self.del_message(msgid)

    def messages(self):
        """
        Returns a generator used for catalog entries iteration.
        """
        for (msgid, translations_dict) in self.cat._messages.items():
            yield (msgid, translations_dict)

    ##### OTHER | PRIVATE #####
    # could we get rid of this if we normalize the format (byte string/unicode)?
    def _get_message_key(self, message):
        for (msgid, translations) in self.messages():
            if msgid == message:
                return message
        # A message may be stored as unicode or byte string
        encoding = HTTPRequest.default_encoding
        if isinstance(message, unicode):
            message = message.encode(encoding)
        else:
            message = unicode(message, encoding)
        for (msgid, translations) in self.messages():
            if msgid == message:
                return message
        return None

class NyMessageCatalog(SimpleItem):
    """Stores messages and their translations"""
    implements(INyTranslationCatalog)


    def __init__(self, id, title, languages=('en', )):

        self.id = id
        self.title = title

        # Language Manager data
        self._languages = tuple(languages)
        self._default_language = self._languages[0]

        # Here the message translations are stored
        self._messages = PersistentMapping()
        self._po_headers = {}

    ### INyTranslationCatalog

    def edit_message(self, msgid, lang, translation):
        # language existance test **not present in Localizer**:
        if lang not in self.get_languages():
            return
        # Add-by-edit functionality **not present in Localizer**:
        if not self._message_exists(msgid):
            self.gettext(msgid, lang)
        self._messages[msgid][lang] = translation

    def del_message(self, msgid):
        """ """
        if self._messages.has_key(msgid):
            del self._messages[msgid]

    def gettext(self, msgid, lang=None, default=None):
        """Returns the corresponding translation of msgid in Catalog.
        """
        if not isinstance(msgid, (str, unicode)):
            raise TypeError, 'only strings can be translated.'
        msgid = msgid.strip()
        # empty message is translated as empty message, regardless of lang
        if not msgid:
            return msgid
        # default `default translation` is the msgid itself
        if default is None:
            default = msgid
        if lang is None:
        # Negotiate lang / rare: translation without ITranslationDomain utility!
            if getSite() is not None:
                i18n_tool = getSite().getPortalI18n()
            else:
                i18n_tool = self.getSite().getPortalI18n()
            lang = i18n_tool.get_negotiator().getLanguage(
                    i18n_tool.get_portal_lang_manager().getAvailableLanguages())

        if lang not in self.get_languages():
            # we don't have that lang, thus we can't translate and won't add msg
            return default

        # Add it if it's not in the dictionary
        if not self._message_exists(msgid):
            self._messages[msgid] = PersistentMapping()

        if not self._messages[msgid].has_key(self._default_language):
            self._messages[msgid][self._default_language] = default

        # translation may be blank (supposition), then-> default (usually msgid)
        in_catalog = self._messages[msgid].get(lang, '')
        return in_catalog or default

    def get_languages(self):
        """Get available languages"""
        return self._languages

    def add_language(self, lang):
        """Add language"""
        if lang not in self._languages:
            self._languages = self._languages + (lang, )

    def del_language(self, lang):
        """Delete language with corresponding messages"""
        if lang not in self.get_languages():
            return
        langlist = list(self._languages)
        langlist.pop(langlist.index(lang))
        self._languages = tuple(langlist)

    def clear(self):
        """Erase all messages"""
        self._messages.clear()

    def messages(self):
        """
        Returns a generator used for catalog entries iteration.
        """
        for (msgid, translations_dict) in self._messages.items():
            yield (msgid, translations_dict)

    ##### OTHER | PRIVATE #####
    # could we get rid of this if we normalize the format (byte string/unicode)?
    def _get_message_key(self, message):
        for (msgid, translations) in self.messages():
            if msgid == message:
                return message
        # A message may be stored as unicode or byte string
        encoding = HTTPRequest.default_encoding
        if isinstance(message, unicode):
            message = message.encode(encoding)
        else:
            message = unicode(message, encoding)
        for (msgid, translations) in self.messages():
            if msgid == message:
                return message
        return None

    def _message_exists(self, message):
        return self._messages.has_key(message)

InitializeClass(LocalizerMessageCatalog)
InitializeClass(NyMessageCatalogAdapter)
