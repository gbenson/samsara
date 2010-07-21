import threading
from samsara import server

class SamsaraHandler(server.HandlerClass):
    """Generate the debugging and control page
    """
    prefix = "samsara/"

    def handle(self, r):
        if not r.uri.startswith(self.prefix):
            return
        uri = r.uri[len(self.prefix):]

        if uri == "shutdown":
            r.type = "text/plain"
            r.payload = "Bye!"
            r.__del__ = Shutdown(self.server.httpserver)

class Shutdown:
    def __init__(self, server):
        self.server = server

    def __call__(self):
        threading.Thread(target = self.server.shutdown).start()
