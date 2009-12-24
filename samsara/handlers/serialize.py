from samsara import server

class XMLSerializer(server.HandlerClass):
    """Serialize XML data
    """
    priority = -75

    xhtmlns = "http://www.w3.org/1999/xhtml"
    rubbish = 'xmlns:ssr="http://inauspicious.org/samsara"'

    def handle(self, r):
        if r.type != "text/xml":
            return
        doc = r.payload
        r.payload = doc.serialize("utf-8", 1).replace(" " + self.rubbish, "")
        r.type = "text/html"
        doc.freeDoc()

        if not r.payload.rstrip().endswith("</rss>"):
            hunt = 'xmlns="%s"' % self.xhtmlns
            found = r.payload.find('xmlns')
            assert found != -1 and r.payload[found:found + len(hunt)] == hunt
            assert r.payload.find('xmlns', found + len(hunt)) == -1
