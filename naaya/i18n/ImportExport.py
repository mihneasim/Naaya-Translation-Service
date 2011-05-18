
# Python imports
from time import gmtime, time

# Empty header information for PO files (UTF-8 is the default encoding)
empty_po_header = {'last_translator_name': '',
                   'last_translator_email': '',
                   'language_team': '',
                   'charset': 'UTF-8'}

class TranslationsImportExport(object):


    def __init__(self, catalog):
        self._catalog = catalog

    def backslashescape(self, x):
        trans = [('"', '\\"'), ('\n', '\\n'), ('\r', '\\r'), ('\t', '\\t')]
        for a, b in trans:
            x = x.replace(a, b)
        return x


    def get_po_header(self, lang):
        """ """
        # For backwards compatibility
        #if not hasattr(aq_base(self), '_po_headers'):
        #    self._po_headers = PersistentMapping()

        return self._catalog._po_headers.get(lang, empty_po_header)

    ### Export methods:
    def export_po(self, lang):
        """Exports the content of the message catalog either to a template
        file (locale.pot) or to an language specific PO file (<x>.po).
        """
        # Get the PO header info
        header = self.get_po_header(lang)
        last_translator_name = header['last_translator_name']
        last_translator_email = header['last_translator_email']
        language_team = header['language_team']
        charset = header['charset']

        # PO file header, empty message.
        po_revision_date = strftime('%Y-%m-%d %H:%m+%Z', gmtime(time()))
        pot_creation_date = po_revision_date
        last_translator = '%s <%s>' % (last_translator_name,
                                       last_translator_email)

        if lang == 'locale.pot':
            language_team = 'LANGUAGE <LL@li.org>'
        else:
            language_team = '%s <%s>' % (lang, language_team)

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
        if lang == 'locale.pot':
            for (k, transdict) in self._catalog.messages():
                d[k] = ""
        else:
            for k, v in self._catalog.messages():
                # don't export bad messages
                if not isinstance(k, unicode):
                    try:
                        k.decode('ascii')
                    except UnicodeDecodeError:
                        continue
                d[k] = v.get(lang, '')

        # Generate the file
        # Generate sorted msgids to simplify diffs
        dkeys = d.keys()
        dkeys.sort(key=lambda key: (isinstance(key,unicode) and key.encode('utf-8') or key))
        for k in dkeys:
            r.append('msgid "%s"' % self.backslashescape(k))
            v = d[k]
            r.append('msgstr "%s"' % self.backslashescape(v))
            r.append('')

        r2 = []
        for x in r:
            if isinstance(x, unicode):
                r2.append(x.encode(charset))
            else:
                r2.append(x)

        return '\n'.join(r2)

    def export_xliff(self, lang, export_all=1):
        """ Exports the content of the message catalog to an XLIFF file
        """
        orglang = self._catalog._default_language
        from DateTime import DateTime
        from Products.Localizer.MessageCatalog import md5text
        from cgi import escape
        r = []
        # alias for append function. For optimization purposes
        r_append = r.append
        # Generate the XLIFF file header
        RESPONSE.setHeader('Content-Type', 'text/xml; charset=UTF-8')
        RESPONSE.setHeader('Content-Disposition',
                           'attachment; filename="%s_%s_%s.xlf"' % (self.id,
                                                                    orglang,
                                                                    lang))

        r_append('<?xml version="1.0" encoding="UTF-8"?>')
        # Version 1.1 of the DTD is not yet available - use version 1.0
        r_append('<!DOCTYPE xliff SYSTEM "http://www.oasis-open.org/committees/xliff/documents/xliff.dtd">')
        # Force a UTF-8 char in the start
        r_append(u'<!-- XLIFF Format Copyright \xa9 OASIS Open 2001-2003 -->')
        r_append('<xliff version="1.0">')
        r_append('<file')
        r_append('original="/%s"' % self.absolute_url(1))
        r_append('product-name="Localizer"')
        r_append('product-version="1.1.x"')
        r_append('datatype="plaintext"')
        r_append('source-language="%s"' % orglang)
        r_append('target-language="%s"' % lang)
        r_append('date="%s"' % DateTime().HTML4())
        r_append('>')
        r_append('<header>')
#       r_append('<phase-group>')
#       r_append('<phase ')
#       r_append('phase-name="%s"' % REQUEST.get('phase_name', ''))
#       r_append('process-name="Export"')
#       r_append('tool="Localizer"')
#       r_append('date="%s"' % DateTime().HTML4())
#       r_append('company-name="%s"' % REQUEST.get('company_name', ''))
#       r_append('job-id="%s"' % REQUEST.get('job_id', ''))
#       r_append('contact-name="%s"' % REQUEST.get('contact_name', ''))
#       r_append('contact-email="%s"' % REQUEST.get('contact_email', ''))
#       r_append('/>')
#       r_append('</phase-group>')
        r_append('</header>')
        r_append('<body>')

        # Get the messages, and perhaps its translations.
        d = {}
        for msgkey, transunit in self._messages.items():
            # if export_all=1 export all messages otherwise export
            # only untranslated messages
            try:
                tr_unit = transunit[lang]
            except KeyError:
                tr_unit = ''

            if int(export_all) == 1 or (int(export_all) == 0 and tr_unit == ''):
                d[msgkey] = tr_unit
            else:
                d[msgkey] = ""

            if d[msgkey] == "":
                d[msgkey] = msgkey

        # Generate sorted msgids to simplify diffs
        dkeys = d.keys()
        dkeys.sort()
        for msgkey in dkeys:
            transunit = self._messages[msgkey]
            r_append('<trans-unit id="%s">' % md5text(msgkey))
            r_append(' <source>%s</source>' % escape(msgkey))
            r_append(' <target>%s</target>' % escape(d[msgkey]))
            if transunit.has_key('note') and transunit['note']:
                r_append(' <note>%s</note>' % escape(transunit['note']))
            r_append('</trans-unit>')

        r_append('</body>')
        r_append('</file>')
        r_append('</xliff>')

        r2 = []
        for x in r:
            if isinstance(x, unicode):
                r2.append(x.encode('utf-8'))
            else:
                r2.append(x)

        return '\r\n'.join(r2)
