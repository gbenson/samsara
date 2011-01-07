import os
from samsara import server

class XMLStyler(server.HandlerClass):
    """Apply stylesheets to XML data
    """
    priority = -50

    def handle(self, r):
        if r.type != "text/xml":
            return
        style = self.getStylesheetPI(r.payload)
        if style is None:
            return
        dir, file = os.path.split(r.uri)
        if file.startswith("index."):
            uri = dir + os.sep
        else:
            uri = r.uri
        if not uri.startswith(os.sep):
            uri = os.sep + uri
        style = os.path.normpath(os.path.join(self.root, dir, style))
        doc = r.payload
        r.payload = self.xmlctx.applyStylesheet(doc, style, {"uri": uri})
        doc.freeDoc()

    def getStylesheetPI(self, doc):
        node = doc.children
        while node:
            if node.type == "pi" and node.name == "xml-stylesheet":
                pi = node.getContent()
                break
            node = node.next
        else:
            return
        # XXX could parse this properly
        assert pi.startswith('href="') and pi.endswith('" type="text/xsl"')
        style = pi[6:-17]
        assert style.find('"') == -1
        return style
