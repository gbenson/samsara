import unittest
from samsara import server

class RequestTest(unittest.TestCase):
    """Class to test samsara.sources.common.Request
    """
    def testNothingServe(self):
        self.assertRaises(ValueError, server.Request, "")
