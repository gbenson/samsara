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

class TestCase(unittest.TestCase):
    """Base class for all data-sourcing handler testcases
    """
    mtimes = {}

    def setUp(self):
        self.dir = os.path.join(test_dir, self.dir)
        self.handler = self.handler(self.dir, context.XMLContext())
        for file in self.mtimes.keys():
            path = os.path.join(self.dir, file)
            if os.path.exists(path):
                t = time.mktime(time.strptime(self.mtimes[file], "%d/%m/%Y"))
                os.utime(path, (t, t))

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
            r.data = intercept.intercept(intercept.STDOUT,
                                         r.xml.debugDumpDocument, None)[1]
            expected = debug_trim_re.sub(r"\1...", expected)

        self.assertEqual(r.data, expected)

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
