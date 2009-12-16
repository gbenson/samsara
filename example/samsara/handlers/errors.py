import os
import re
import samsara.server

class ErrorHandler(samsara.server.HandlerClass):
    uri_re = re.compile(r"^(\d{3})\.shtml$")
    
    def __init__(self, *args):
        samsara.server.HandlerClass.__init__(self, *args)
        self.registerDocument(os.path.join(self.root, "errors.xml"), "db")
        self.xsl = os.path.join(self.root, "errors.xsl")

    def handle(self, r):
        match = self.uri_re.match(r.uri)
        if not match:
            return
        code = match.group(1)
        if not self.db.xpathEval("/errors/error[@code = '%s']" % code):
            return
        r.payload = self.xmlctx.applyStylesheet(
            self.db, self.xsl, {"code": code})
        r.payload.setBase(os.path.join(self.root, r.uri))
        r.type = "text/xml"

class LinkRewriter(samsara.server.HandlerClass):
    # Errors can occur anywhere within the directory heirachy.
    # Rather than rewrite the whole site to use absolute links,
    # I'm just going to rewrite them here.
    priority = -100
    href_re = re.compile(r'href="(?!(/|[^"]*:))')

    def handle(self, r):
        match = ErrorHandler.uri_re.match(r.uri)
        if not match:
            return
        r.payload = self.href_re.sub('href="/', r.payload)
