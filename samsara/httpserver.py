import sys
import SocketServer 
import BaseHTTPServer
import urllib
import traceback
from samsara import server

class HTTPServer(SocketServer.TCPServer):
    """HTTP interface to a Samsara server

    Note that this is intrinsically unsuitable for use with a forking
    or threading server: this is intentional, to allow applications to
    be developed without undue complexity.
    """

    allow_reuse_address = 1

    def __init__(self, addr, samsara):
        """Constructor: may be extended, do not override.
        """
        SocketServer.TCPServer.__init__(self, addr, self.RequestHandler)
        self.samsara = samsara
        samsara.httpserver = self

    class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
        """HTTP request handler for the Samsara HTTP server.
        """
        server_version = "Samsara/0.1"

        def sendResponse(self, code, type, body):
            """Send a response with the appropriate headers
            """
            self.send_response(code)
            self.send_header("Content-type", type)
            self.send_header("Content-length", len(body))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            """Serve a GET request
            """
            try:
                r = self.server.samsara.get(urllib.unquote(self.path))
                self.sendResponse(200, r.type, r.getPayload())

            except:
                type, value, tb = sys.exc_info()

                if type == server.NotFoundError:
                    code  = 404
                    title = "Not found"
                    body  = "The page you have requested was not found"
                else:
                    code  = 500
                    title = "Server error"
                    body  = "".join(traceback.format_exception(type,
                                                               value,
                                                               tb))

                self.sendResponse(code, "text/plain", title + "\n\n" + body)

        def log_message(self, *args):
            """Log an arbitrary message
            """
            pass
