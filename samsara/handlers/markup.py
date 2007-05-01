from samsara import server

class MarkupHandler(server.HandlerClass):
    """Mark up XML data
    """
    priority = -50

    xhtmlns = "http://www.w3.org/1999/xhtml"

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

            hunt = 'xmlns="%s"' % self.xhtmlns
            found = r.payload.find('xmlns="')
            assert found != -1 and r.payload[found:found + len(hunt)] == hunt
            assert r.payload.find('xmlns="', found + len(hunt)) == -1
