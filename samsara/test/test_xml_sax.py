import unittest
from samsara.xml import sax

import os
import libxml2
import re
import tempfile

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
            actual = sax.parseXML(doc, Callback()).log
            self.assertEqual(expected, actual)
