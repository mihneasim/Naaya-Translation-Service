
# Python imports
import time
from datetime import datetime
try:
    # python 2.6
    from hashlib import md5
except ImportError:
    # python 2.4
    from md5 import new as md5
from lxml import etree
import codecs
import re

# Empty header information for PO files (UTF-8 is the default encoding)
empty_po_header = {'last_translator_name': '',
                   'last_translator_email': '',
                   'language_team': '',
                   'charset': 'UTF-8'}

class TranslationsImportExport(object):


    def __init__(self, catalog):
        self._catalog = catalog

    def backslash_escape(self, x):
        trans = [('"', '\\"'), ('\n', '\\n'), ('\r', '\\r'), ('\t', '\\t')]
        for a, b in trans:
            x = x.replace(a, b)
        return x

    def backslash_unescape(self, x):
        trans = [('\\"', '"'), ('\\n', '\n'), ('\\r', '\r'), ('\\t', '\t')]
        for a, b in trans:
            x = x.replace(a, b)
        return x

    def get_po_header(self, lang):
        """ """
        # For backwards compatibility
        #if not hasattr(aq_base(self), '_po_headers'):
        #    self._po_headers = PersistentMapping()

        return self._catalog._po_headers.get(lang, empty_po_header)


    ### Export methods ###

    def export_po(self, lang):
        """Exports the content of the message catalog either to a template
        file (locale.pot) or to an language specific PO file (<x>.po).
        """
        # Get the PO header info
        header = self.get_po_header(lang)
        last_translator_name = header['last_translator_name']
        last_translator_email = header['last_translator_email']
        language_team = header['language_team']
        charset = header['charset'] or 'UTF-8'

        # PO file header, empty message.
        po_revision_date = time.strftime('%Y-%m-%d %H:%M+%Z',
                                         time.gmtime(time.time()))
        pot_creation_date = po_revision_date
        last_translator = '%s <%s>' % (last_translator_name,
                                       last_translator_email)

        if lang == 'locale.pot':
            language_team = 'LANGUAGE <LL@li.org>'
        else:
            language_team = '%s <%s>' % (lang, language_team)

        r = ['msgid ""',
             'msgstr "Project-Id-Version: naaya.i18n\\n"',
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
            r.append('msgid "%s"' % self.backslash_escape(k))
            v = d[k]
            r.append('msgstr "%s"' % self.backslash_escape(v))
            r.append('')

        r2 = []
        for x in r:
            if isinstance(x, unicode):
                r2.append(x.encode(charset))
            else:
                r2.append(x)

        return '\n'.join(r2)

    def export_xliff(self, lang, export_all=True):
        """ Exports the content of the message catalog to an XLIFF file
        """
        orglang = self._catalog._default_language
        root = etree.Element("xliff", version="1.0")
        etree.SubElement(root, "file",
                         #original=("/" + self._catalog.absolute_url(1)),
                         datatype="plaintext",
                         date=datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                         **{'source-language': orglang,
                            'target-language': lang,
                            'product-name': 'naaya.i18n',
                            'product-version': '1.0'})
        header = etree.SubElement(root, "header")
        header.text = ""
        body = etree.SubElement(root, "body")

        # For the approved="yes|no" attribute of trans-unit
        unapproved = []
        # Get the messages, and perhaps its translations.
        d = {}
        for msgkey, transunit in self._catalog.messages():
            # if export_all=True export all messages otherwise export
            # only untranslated messages
            tr_unit = transunit.get(lang, '')

            if export_all == True or (export_all == False and tr_unit == ''):
                d[msgkey] = tr_unit
                if d[msgkey] == "":
                    unapproved.append(msgkey)
                    d[msgkey] = msgkey

        # Generate sorted msgids to simplify diffs
        dkeys = d.keys()
        dkeys.sort()
        for msgkey in dkeys:
            approved = "yes"
            if msgkey in unapproved:
                approved = "no"
            #if isinstance(d[msgkey], unicode):
            #    d[msgkey] = d[msgkey].encode('utf-8')
            #if isinstance(msgkey, unicode):
            #    msgkey = msgkey.encode('utf-8')

            tr_unit = etree.SubElement(body, "trans-unit",
                                       id=md5(msgkey.encode('utf-8')).hexdigest(),
                                       approved=approved)
            source = etree.SubElement(tr_unit, "source")
            source.text = msgkey
            target = etree.SubElement(tr_unit, "target")
            target.set('{http://www.w3.org/XML/1998/namespace}lang', lang.lower())
            if approved == "no":
                target.set("state", "needs-review-translation")
            target.text = d[msgkey]

        return etree.tostring(root, xml_declaration=True, encoding='utf-8',
                              pretty_print=True)

    def export_tmx(self):
        """Exports the content of the message catalog to a TMX file
        """
        orglang = self._catalog._default_language

        # Get the header info
        header = self.get_po_header(orglang)
        charset = header['charset']
        creationtool = 'naaya.i18n'
        creationtoolversion = '1.0'
        creationdate = datetime.now().strftime("%Y%m%dT%H%M%SZ")

        root = etree.Element("tmx", version="1.4")
        #root.docinfo.doctype = '<!DOCTYPE tmx SYSTEM "http://www.lisa.org/tmx/tmx14.dtd" >'
        header = etree.SubElement(root, "header",
                                    datatype='xml',
                                    segtype='block',
                                    srclang=orglang,
                                    adminlang=orglang,
                                    creationtool=creationtool,
                                    creationtoolversion=creationtoolversion,
                                    **{'o-encoding': charset.lower()})
        header.text = ""
        body = etree.SubElement(root, "body")
        # handle messages
        d = {}
        filename = '%s.tmx' % self._catalog.title
        for msgkey, transunit in self._catalog.messages():
            tu = etree.SubElement(body, "tu", creationtool=creationtool,
                                  creationtoolversion=creationtoolversion,
                                  tuid=md5(msgkey.encode('utf-8')).hexdigest(),
                                  creationdate=creationdate)
            for lang in transunit.keys():
                if not transunit[lang]:
                    transunit[lang] = msgkey
                tuv = etree.SubElement(tu, "tuv",
                                       creationdate=creationdate)
                tuv.set('{http://www.w3.org/XML/1998/namespace}lang', lang.lower())
                seg = etree.SubElement(tuv, "seg")
                seg.text = transunit[lang]
            for all_langs in self._catalog.get_languages():
                if all_langs not in transunit.keys():
                    tuv = etree.SubElement(tu, "tuv",
                                           creationdate=creationdate)
                    tuv.set('{http://www.w3.org/XML/1998/namespace}lang', all_langs.lower())
                    seg = etree.SubElement(tuv, "seg")
                    seg.text = msgkey
        return etree.tostring(root, xml_declaration=True, encoding=charset,
                              pretty_print=True) 


    ### Import methods ###

    def import_po(self, lang, filehandler):

        # Load the data
        line = filehandler.readline()
        BEFORE_HEADER = 0; IN_HEADER = 1; IN_MAPPINGS = 2
        encoding_pat = re.compile(r'charset=([a-z0-9-]*)', re.IGNORECASE)
        msgid_pat = re.compile(r'^msgid[\t\s]+"(.*?)"$', re.IGNORECASE)
        msgstr_pat = re.compile(r'^msgstr[\t\s]+"(.*?)"$', re.IGNORECASE)
        state = BEFORE_HEADER
        encoding = None
        msgid = None
        data = {}
        cnt = 0
        while line:
            cnt += 1
            line = line.strip()
            if line:
                if state is BEFORE_HEADER:
                    if line == 'msgid ""':
                        state = IN_HEADER
                elif state is IN_HEADER:
                    enc = encoding_pat.search(line)
                    if enc is not None:
                        encoding = enc.groups()[0]
                        if encoding.lower() not in ('utf8', 'utf-8'):
                            raise ValueError("Only import utf-8 encoded files")
                        state = IN_MAPPINGS
                elif state is IN_MAPPINGS:
                    if encoding is None:
                        raise ValueError(("Missing encoding specification in"
                                          " PO headers. "
                                          "Only import utf-8 encoded files"))
                    if msgid is not None and line.startswith('msgstr '):
                        match = msgstr_pat.search(line)
                        if match is None:
                            raise ValueError("Error reading msgstr at line %d"
                                             % cnt)
                        else:
                            data[msgid] = match.groups()[0]
                            msgid = None
                    match = msgid_pat.search(line)
                    if match is not None:
                        msgid = match.groups()[0]
                else:
                    raise Error('Undefined state in parsing .po file')
            line = filehandler.readline()

        filehandler.close()
        for (msgid, msgstr) in data.items():
            # TODO: do not replace with empty messages
            self._catalog.edit_message(
                               self.backslash_unescape(msgid).decode(encoding),
                               lang,
                               self.backslash_unescape(msgstr).decode(encoding))
