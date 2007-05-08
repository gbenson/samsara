import os
from samsara import server

class StyleHandler(server.HandlerClass):
    """Apply stylesheets to XML data
    """
    priority = -50

    def handle(self, r):
        if r.type != "text/xml":
            return
        dir, file = os.path.split(r.uri)
        if file.startswith("index."):
            uri = dir + os.sep
        else:
            uri = r.uri
        if not uri.startswith(os.sep):
            uri = os.sep + uri
        doc = r.payload
        r.payload = self.xmlctx.applyStylesheetPI(doc, {"uri": uri})
        doc.freeDoc()
