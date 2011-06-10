
# Python imports

# Zope imports
from Globals import PersistentMapping, InitializeClass
from OFS.SimpleItem import SimpleItem
from Persistence import Persistent
from ZPublisher import HTTPRequest
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from zope.app.component.hooks import getSite

# Product imports
from interfaces import INyTranslationCatalog

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


class NyMessageCatalog(Persistent):
    """Stores messages and their translations"""

    implements(INyTranslationCatalog)

    security = ClassSecurityInfo()

    def __init__(self, id, title, languages=('en', )):

        self.id = id
        self.title = title

        # Language Manager data
        self._languages = tuple(languages)
        self._default_language = self._languages[0]

        # Here the message translations are stored
        self._messages = PersistentMapping()
        self._po_headers = PersistentMapping()

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

    security.declarePublic('gettext')
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
            import pdb; pdb.set_trace()
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
            update_transaction_note()

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


    def _message_exists(self, message):
        return self._messages.has_key(message)

    ##### OTHER | PRIVATE #####
    # could we get rid of this if we normalize the format (byte string/unicode)?
    def _get_message_key(self, message):
        if self._message_exists(message):
            return message
        # A message may be stored as unicode or byte string
        encoding = HTTPRequest.default_encoding
        if isinstance(message, unicode):
            message = message.encode(encoding)
        else:
            message = unicode(message, encoding)
        if self._message_exists(message):
            return message
        return None

InitializeClass(NyMessageCatalog)
