from samsara import server

class StyleHandler(server.HandlerClass):
    """Apply stylesheets to XML data
    """
    priority = -50

    def handle(self, r):
        if r.type == "text/xml":
            doc = r.payload
            r.payload = self.xmlctx.applyStylesheetPI(doc)
            doc.freeDoc()
