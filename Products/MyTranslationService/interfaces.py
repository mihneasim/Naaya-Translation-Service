# Zope imports
from zope.interface import Interface, Attribute

class ITranslationCatalog(Interface):
    
    __call__ = Attribute("""Must be set to address of gettext method""")
    meta_type = Attribute("""Meta type of catalog""")
    security = Attribute("""Security Info""")
    
    # Should it be here?
    #manage_messages
    #manage_propertiesForm
    #manage_Import_form
    #manage_Export_form
    #hasmsg
    #hasLS
    
    def message_exists(message):
        """ """

    def message_edit(message, language, translation, note):
        """ """

    def message_del(self, message):
        """ """

    def gettext(message, lang=None, add=1, default=None):
        """Returns the message translation from the database if available.

        If add=1, add any unknown message to the database.
        If a default is provided, use it instead of the message id
        as a translation for unknown messages.
        """

    def translate(domain, msgid, *args, **kw):
        """This method is required to get the i18n namespace from ZPT working.
        """

    def manage_options():
        """Return available management screens"""

    #######################################################################
    # Management screens -- Messages
    #######################################################################

    def get_namespace(REQUEST):
        """For the management interface, allows to filter the messages to
        show.
        """

    def manage_editMessage(message, language, translation, note,
                           REQUEST, RESPONSE):
        """Modifies a message.
        """
    
    def manage_delMessage(message, REQUEST, RESPONSE):
        """ """

    #######################################################################
    # Management screens -- Properties
    # Management screens -- Import/Export
    # FTP access
    #######################################################################

    def manage_properties(title, REQUEST=None, RESPONSE=None):
        """Change the Message Catalog properties.
        """

    def get_po_header(lang):
        """ """

    def update_po_header(lang,
                         last_translator_name=None,
                         last_translator_email=None,
                         language_team=None,
                         charset=None,
                         REQUEST=None, RESPONSE=None):
        """ """

    def get_charsets():
        """ """

    def manage_export(x, REQUEST=None, RESPONSE=None):
        """Exports the content of the message catalog either to a template
        file (locale.pot) or to an language specific PO file (<x>.po).
        """

    def po_import(lang, data):
        """ """

    def manage_import(lang, file, REQUEST=None, RESPONSE=None):
        """ For backwards compatibility only, use "po_import" instead. """

    def objectItems(spec=None):
        """ """

    def tmx_export(REQUEST, RESPONSE=None):
        """Exports the content of the message catalog to a TMX file
        """

    def tmx_import(howmuch, file, REQUEST=None, RESPONSE=None):
        """Imports a TMX level 1 file.
        """

    #######################################################################
    # Backwards compatibility (XXX)
    #######################################################################

    def xliff_export(x, export_all=1, REQUEST=None, RESPONSE=None):
        """Exports the content of the message catalog to an XLIFF file
        """

    def xliff_import(howmuch, file, REQUEST=None):
        """XLIFF is the XML Localization Interchange File Format designed by a
        group of software providers.  It is specified by www.oasis-open.org
        """