from samsara import server

class MarkupHandler(server.HandlerClass):
    """Mark up XML data
    """
    priority = -50

    def handle(self, r):
        if r.xml is not None:
            doc = self.xmlctx.applyStylesheetPI(r.xml)
            try:
                r.data = doc.serialize("ISO-8859-1", 1)
                r.type = "text/html"

            finally:
                doc.freeDoc()
