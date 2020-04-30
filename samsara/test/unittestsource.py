import unittest
from samsara import server

import sys
import os
import re
import time
from samsara.util import intercept
from samsara.xml import context

samsara_dir = os.path.split(os.path.split(os.path.abspath(sys.argv[0]))[0])[0]
test_dir = os.path.join(samsara_dir, "samsara", "test", "sources")

# libxml2 trims long lines in debug dumps, so we try to match it
debug_trim_re = re.compile("^(\s*\w+?=.{40}).*$", re.MULTILINE)

class FakeServer(object):
    def __init__(self, root):
        self.root = os.path.realpath(root)
        self.xmlctx = context.XMLContext()

    def __call__(self):
        return self

class TestCase(unittest.TestCase):
    """Base class for all data-sourcing handler testcases
    """

    def setUp(self):
        self.dir = os.path.join(test_dir, self.dir)
        self.handler = self.handler(FakeServer(self.dir))

    def checkSuccess(self, uri, type, expected):
        """Apply a series of tests to what should be a successful request
        """
        r = server.Request(uri)
        save_uri = r.uri
        self.handler.handle(r)
        self.assertEqual(r.uri, save_uri)
        self.failUnlessEqual(r.type, type)

        if r.type == "text/xml":
            # Bloody libxml2, no function to _return_ anything, just
            # stuff to print it out.  Oh, and I have no idea what the
            # parameter to debugDumpDocument is. It's a FILE * in the
            # C one, but here?
            r.payload = intercept.intercept(
                intercept.STDOUT, r.payload.debugDumpDocument, None)[1]
            r.type = "text/plain"
            expected = debug_trim_re.sub(r"\1...", expected)

        self.assertEqual(r.getPayload(), expected)

    def checkDeclined(self, uri):
        """Apply a series of tests to what should be a failed request
        """
        r = server.Request(uri)
        save_uri = r.uri
        self.handler.handle(r)
        self.assertEqual(r.uri, save_uri)
        self.assertEqual(r.type, None)

    def checkRewrite(self, uri, new_uri):
        """Apply a series of tests to what should be a rewritten request
        """
        r = server.Request(uri)
        self.handler.handle(r)
        self.assertEqual(r.uri, new_uri[1:])
        self.assertEqual(r.type, None)
