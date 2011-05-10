
# Python imports
from time import gmtime, time

# Zope imports
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

# Empty header information for PO files (UTF-8 is the default encoding)
empty_po_header = {'last_translator_name': '',
                   'last_translator_email': '',
                   'language_team': '',
                   'charset': 'UTF-8'}

class TranslationsImportExport(object):

    security = ClassSecurityInfo()

    def __init__(self, catalog):
        self.catalog = catalog

    def backslashescape(self, x):
        trans = [('"', '\\"'), ('\n', '\\n'), ('\r', '\\r'), ('\t', '\\t')]
        for a, b in trans:
            x = x.replace(a, b)
        return x


    security.declareProtected('View management screens', 'get_po_header')
    def get_po_header(self, lang):
        """ """
        # For backwards compatibility
        #if not hasattr(aq_base(self), '_po_headers'):
        #    self._po_headers = PersistentMapping()

        return self.catalog._po_headers.get(lang, empty_po_header)

    ### Export methods:
    security.declarePublic('manage_export')
    def manage_export(self, x, REQUEST=None, RESPONSE=None):
        """Exports the content of the message catalog either to a template
        file (locale.pot) or to an language specific PO file (<x>.po).
        """
        # Get the PO header info
        header = self.get_po_header(x)
        last_translator_name = header['last_translator_name']
        last_translator_email = header['last_translator_email']
        language_team = header['language_team']
        charset = header['charset']

        # PO file header, empty message.
        po_revision_date = strftime('%Y-%m-%d %H:%m+%Z', gmtime(time()))
        pot_creation_date = po_revision_date
        last_translator = '%s <%s>' % (last_translator_name,
                                       last_translator_email)

        if x == 'locale.pot':
            language_team = 'LANGUAGE <LL@li.org>'
        else:
            language_team = '%s <%s>' % (x, language_team)

        r = ['msgid ""',
             'msgstr "Project-Id-Version: %s\\n"' % self.title,
             '"POT-Creation-Date: %s\\n"' % pot_creation_date,
             '"PO-Revision-Date: %s\\n"' % po_revision_date,
             '"Last-Translator: %s\\n"' % last_translator,
             '"Language-Team: %s\\n"' % language_team,
             '"MIME-Version: 1.0\\n"',
             '"Content-Type: text/plain; charset=%s\\n"' % charset,
             '"Content-Transfer-Encoding: 8bit\\n"',
             '', '']

        # Get the messages, and perhaps its translations.
        d = {}
        if x == 'locale.pot':
            filename = x
            for (k, transdict) in self.catalog.messages():
                d[k] = ""
        else:
            filename = '%s.po' % x
            for k, v in self.catalog.messages():
                # don't export bad messages
                if not isinstance(k, unicode):
                    try:
                        k.decode('ascii')
                    except UnicodeDecodeError:
                        continue
                d[k] = v.get(x, '')

        # Generate the file
        # Generate sorted msgids to simplify diffs
        dkeys = d.keys()
        dkeys.sort(key=lambda key: (isinstance(key,unicode) and key.encode('utf-8') or key))
        for k in dkeys:
            r.append('msgid "%s"' % self.backslashescape(k))
            v = d[k]
            r.append('msgstr "%s"' % self.backslashescape(v))
            r.append('')

        if RESPONSE is not None:
            RESPONSE.setHeader('Content-type', 'application/data')
            RESPONSE.setHeader('Content-Disposition',
                               'inline;filename=%s' % filename)

        r2 = []
        for x in r:
            if isinstance(x, unicode):
                r2.append(x.encode(charset))
            else:
                r2.append(x)

        return '\n'.join(r2)

InitializeClass(TranslationsImportExport)
