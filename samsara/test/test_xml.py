import unittest
from samsara.util import xml

import os
import libxml2
import re
import tempfile

# Test the XSLT stuff

stylesheet = '''\
<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match="basic-test">
    <match>This is <xsl:value-of select="test/filename"/> speaking</match>
  </xsl:template>
  <xsl:template match="test">
    This shouldn\'t be here
  </xsl:template>
</xsl:stylesheet>
'''

document = '''\
<?xml version="1.0"?>
<basic-test>
  <test>
    <filename>test_markup.py</filename>
  </test>
</basic-test>
'''

documentPI = '''\
<?xml version="1.0"?>
<?xml-stylesheet href="%s" type="text/xsl"?>
<basic-test>
  <test>
    <filename>test_markup.py</filename>
  </test>
</basic-test>
'''

expected = '''<?xml version="1.0"?>
<match>This is test_markup.py speaking</match>
'''

class TestApplyStylesheet(unittest.TestCase):
    def setUp(self):
        self.sspath = tempfile.mktemp()
        self.doc = libxml2.parseDoc(document)

    def tearDown(self):
        self.doc.freeDoc()
        os.unlink(self.sspath)
    
    def doTest(self, doc, stylesheet):
        open(self.sspath, "w").write(stylesheet)
        res = xml.applyStylesheet(doc, self.sspath)
        try:
            out = tempfile.mktemp()
            try:
                res.saveFile(out)
                return open(out).read()
            finally:
                os.unlink(out)
        finally:
            res.freeDoc()

    def testNormal(self):
        actual = self.doTest(self.doc, stylesheet)
        self.assertEqual(expected, actual)

    def testMalformedStylesheet(self):
        bork = "bork" + stylesheet
        self.assertRaises(libxml2.parserError, self.doTest, self.doc, bork)

    def testBadXSLT(self):
        bork = re.compile("xsl:value-of").sub("xsl:eat-this", stylesheet)
        self.assertRaises(xml.XMLError, self.doTest, self.doc, bork)


class TestApplyStylesheetPI(unittest.TestCase):
    def setUp(self):
        self.sspath = tempfile.mktemp()
        self.doc = libxml2.parseDoc(documentPI % self.sspath)
        self.borkdoc = libxml2.parseDoc(documentPI % "/where/is/it")

    def tearDown(self):
        self.doc.freeDoc()
        self.borkdoc.freeDoc()
        os.unlink(self.sspath)
    
    def doTest(self, doc, stylesheet):
        open(self.sspath, "w").write(stylesheet)
        res = xml.applyStylesheetPI(doc)
        try:
            out = tempfile.mktemp()
            try:
                res.saveFile(out)
                return open(out).read()
            finally:
                os.unlink(out)
        finally:
            res.freeDoc()

    def testNormal(self):
        actual = self.doTest(self.doc, stylesheet)
        self.assertEqual(expected, actual)

    def testCantFindStylesheet(self):
        self.assertRaises(xml.XMLError, self.doTest, self.borkdoc, stylesheet)

    def testMalformedStylesheet(self):
        bork = "bork" + stylesheet
        self.assertRaises(xml.XMLError, self.doTest, self.doc, bork)

    def testBadXSLT(self):
        bork = re.compile("xsl:value-of").sub("xsl:eat-this", stylesheet)
        self.assertRaises(xml.XMLError, self.doTest, self.doc, bork)

# Test the SAX stuff

class Callback:
    def __init__(self):
        self.log = []

    def startDocument(self):
        self.log.append("startDocument")

    def endDocument(self):
        self.log.append("endDocument")

    def startElement(self, tag, attrs):
        self.log.append("startElement %s %s" % (tag, attrs))

    def endElement(self, tag):
        self.log.append("endElement %s" % tag)

    def characters(self, data):
        self.log.append("characters %s" % data)

    def processingInstruction(self, target, data):
        self.log.append("processingInstruction %s %s" % (target, data))


class TestParseXML(unittest.TestCase):
    cases = (("", []),
             ("<foo url='tst'>bar</foo>",
              ["startDocument",
               "startElement foo {'url': 'tst'}",
               "characters bar",
               "endElement foo",
               "endDocument"]),
             ("<?xml-foo bar='baz' spam='eggs'?><foo url='tst'>bar</foo>",
              ["startDocument",
               "processingInstruction xml-foo bar='baz' spam='eggs'",
               "startElement foo {'url': 'tst'}",
               "characters bar",
               "endElement foo",
               "endDocument"]))

    def testDocuments(self):
        for doc, expected in self.cases:
            actual = xml.saxParseXML(doc, Callback()).log
            self.assertEqual(expected, actual)
