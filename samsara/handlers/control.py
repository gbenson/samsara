import libxml2
import operator
import os
import sys
import threading
from samsara import server

class SamsaraHandler(server.HandlerClass):
    """Generate the debugging and control page
    """
    priority = -45
    prefix = "samsara/"

    def __init__(self, *args):
        server.HandlerClass.__init__(self, *args)
        self.style = os.path.join(os.path.dirname(__file__), "samsara.xsl")

    def getHandlers(self):
        handlers = reduce(operator.add, self.server.handlers.values())
        handlers.sort(lambda a, b: b.priority - a.priority)
        return [(handler.priority,
                 handler,
                 os.path.realpath(sys.modules[handler.__module__].__file__) \
                     .rstrip("c").replace(os.environ["HOME"], "~"))
                for handler in handlers]

    def handle(self, r):
        if not r.uri.startswith(self.prefix):
            r.addButton("S", "/samsara/", 0)
            return
        uri = r.uri[len(self.prefix):].rstrip("?")

        doc = libxml2.newDoc("1.0")
        page = doc.newChild(None, "page", None)
        if uri == "":
            handlers = page.newChild(None, "handlers", None)
            for priority, handler, path in self.getHandlers():
                handler = handlers.newChild(None, "handler", None)
                handler.setProp("path", path)
                handler.setProp("priority", str(priority))
            form = page.newChild(None, "form", None)
            form.setProp("action", "shutdown")
            form.newChild(None, "button", "Shutdown")
        if uri == "shutdown":
            page.newChild(None, "message", "Really shut down?")
            form = page.newChild(None, "form", None)
            form.setProp("action", "really-shutdown")
            form.newChild(None, "button", "Yes")
        elif uri == "really-shutdown":
            page.newChild(None, "message", "Bye...")

        r.type = "text/xml"
        r.payload = self.xmlctx.applyStylesheet(doc, self.style)

        if uri == "really-shutdown":
            class Shutdown:
                def __init__(self, server):
                    self.server = server
                def __call__(self):
                    threading.Thread(target = self.server.shutdown).start()
            r.__del__ = Shutdown(self.server.httpserver)
