from samsara import server

class MarkupHandler(server.HandlerClass):
    """Mark up XML data
    """
    priority = -50

    def handle(self, r):
        if r.type == "text/xml":
            node = r.payload.children
            while node:
                if (node.type, node.name) == ("pi", "samsara"):
                    # XXX should parse this properly
                    if node.getContent() != 'output="index.shtml"':
                        raise ValueError, "unhandled directive"
                    r.filename = "index.shtml"
                node = node.next
            doc = self.xmlctx.applyStylesheetPI(r.payload)
            try:
                r.payload.freeDoc()
                r.payload = doc.serialize("utf-8", 1)
                r.type = "text/html"

            finally:
                doc.freeDoc()

            assert r.payload.find('xmlns=""') == -1
