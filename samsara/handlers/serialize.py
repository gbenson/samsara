from samsara import server

class XMLSerializer(server.HandlerClass):
    """Serialize XML data
    """
    priority = -75

    def handle(self, r):
        if r.type != "text/xml":
            return
        doc = r.payload
        r.payload = doc.serialize("utf-8", 1)
        r.type = "text/html"
        doc.freeDoc()
