from samsara import server

class MarkupHandler(server.HandlerClass):
    """Mark up XML data
    """
    priority = -50

    def handle(self, r):
        if r.xml is not None:
            node = r.xml.children
            while node:
                if (node.type, node.name) == ("pi", "samsara"):
                    # XXX should parse this properly
                    if node.getContent() != 'output="index.shtml"':
                        raise ValueError, "unhandled directive"
                    r.filename = "index.shtml"
                node = node.next
            doc = self.xmlctx.applyStylesheetPI(r.xml)
            try:
                r.data = doc.serialize("ISO-8859-1", 1)
                r.type = "text/html"

            finally:
                doc.freeDoc()
