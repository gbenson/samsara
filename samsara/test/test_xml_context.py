import unittest
from samsara.xml import context

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
        res = context.applyStylesheet(doc, self.sspath)
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
        self.assertRaises(context.XMLError, self.doTest, self.doc, bork)


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
        res = context.applyStylesheetPI(doc)
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
        self.assertRaises(context.XMLError, self.doTest, self.borkdoc, stylesheet)

    def testMalformedStylesheet(self):
        bork = "bork" + stylesheet
        self.assertRaises(context.XMLError, self.doTest, self.doc, bork)

    def testBadXSLT(self):
        bork = re.compile("xsl:value-of").sub("xsl:eat-this", stylesheet)
        self.assertRaises(context.XMLError, self.doTest, self.doc, bork)