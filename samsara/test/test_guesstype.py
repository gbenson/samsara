import unittest
from samsara.util import guesstype

class KnownValues(unittest.TestCase):
    knownValues = (("foo",        "text/plain",         "text/plain"),
                   ("foo/bar",    "text/plain",         "text/plain"),
                   ("/foo/bar",   "text/plain",         "text/plain"),
                   ("/foo/bar/",  "text/plain",         "text/plain"),
                   ("foo/xml",    "text/plain",         "text/plain"),
                   ("foo.xml",    "text/xml",           "text/xml"),
                   ("foo.html",   "text/html",          "text/html"),
                   ("foo.tar.gz", "application/x-gzip", "application/x-tar"))

    def testKnownValues(self):
        for path, outer, inner in self.knownValues:
            self.assertEqual(outer, guesstype.guessType(path))
            self.assertEqual(inner, guesstype.guessBaseType(path))
