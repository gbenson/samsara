import unittest
from samsara import httpserver

import sys
import os
import socket
import httplib
from samsara import server

host = "localhost"
port = 9000

class ChildDiedError:
    pass

class TestException:
    pass

class TestResponse:
    def __init__(self, type, data):
        self.type = type
        self.data = data

    def getPayload(self):
        return self.data

class TestSamsaraServer:
    def get(self, uri):
        if uri == "/200":
            return TestResponse("text/plain", "Ok")
        elif uri == "/404":
            raise server.NotFoundError("%s not found" % uri)
        elif uri == "/500":
            raise TestException
        else:
            return TestResponse("text/plain", "NOT OK")

responses = {200: "Ok",
             404: "Not found\n\nThe page you have requested was not found",
             500: "Server error\n\nTraceback (most recent call last):\n"}

class HTTPServerTestCase(unittest.TestCase):
    def setUp(self):
        # XXX: Sockets in Python don't seem to close gracefully, and
        # you have to wait for something to timeout after the app
        # exits -- too bad if you are running the same app in close
        # succession. We just try port after port until we get one
        self.host = host
        self.port = port
        s = TestSamsaraServer()
        while 1:
            try:
                self.httpd = httpserver.HTTPServer((self.host, self.port), s)
                break

            except socket.error:
                if str(sys.exc_value) != "(98, 'Address already in use')":
                    raise
                self.port = self.port + 1

    def forkAndServeOnce(self):
        self.pid = os.fork()
        if self.pid == 0:
            try:
                self.httpd.handle_request()
            finally:
                os._exit(0)

    def waitForChild(self):
        status = os.waitpid(self.pid, 0)[1]
        if not os.WIFEXITED(status) or os.WEXITSTATUS(status) != 0:
            raise ChildDiedError

    def doOneTest(self, code):
        expected = responses[code]

        self.forkAndServeOnce()
        conn = httplib.HTTPConnection(self.host, self.port)
        conn.request("GET", "/%d" % code)
        resp = conn.getresponse()
        resp.begin()

        self.assertEqual(code, resp.status)

        actual = resp.read()
        self.failUnless(resp.isclosed())
        self.waitForChild()

        self.assertEqual(expected, actual[:len(expected)])

    def testServer(self):
        for test in responses.keys():
            self.doOneTest(test)
