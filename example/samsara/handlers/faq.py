import os
import samsara.server

class FaqHandler(samsara.server.HandlerClass):
    def __init__(self, *args):
        samsara.server.HandlerClass.__init__(self, *args)
        self.registerDocument(os.path.join(self.root, "faq.xml"), "db")
        self.index_xsl = os.path.join(self.root, "faq-index.xsl")
        self.entry_xsl = os.path.join(self.root, "faq-entry.xsl")

    def handle(self, r):
        if not r.uri.endswith(".html"):
            return
        if r.uri == "questions.html":
            style, params = self.index_xsl, {"showAll": "no"}
        elif r.uri == "all-questions.html":
            style, params = self.index_xsl, {"showAll": "yes"}
        else:
            entry = r.uri[:-5].split("-")
            entry[1:] = [element.title() for element in entry[1:]]
            entry = "".join(entry)
            if entry == r.uri[:-5]:
                return
            if not self.db.xpathEval("/faq/entries/entry[@id='%s']" % entry):
                return
            style, params = self.entry_xsl, {"entry": entry}
        r.payload = self.xmlctx.applyStylesheet(self.db, style, params)
        r.payload.setBase(os.path.join(self.root, r.uri))
        r.type = "text/xml"
