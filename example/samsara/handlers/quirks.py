import re
import samsara.server

# An XHTML 1.0 Strict doctype with an XML declaration will cause
# IE6, Opera 7.0 and Konqueror 3.2 to render the page with Quirks
# Mode.  Omitting the XML declaration causes them to use Almost
# Standards Mode, in which everything bar the vertical sizing of
# table cells happens according to the CSS2 specification.
#   -- http://hsivonen.iki.fi/doctype/

class XMLDeclStripper(samsara.server.HandlerClass):
    priority = -100
    strip = re.compile(
        r'^<\?xml\s+version="1.0"\s+encoding="[Uu][Tt][Ff]-8"\s*\?>\s*', re.S)

    def handle(self, r):
        if r.type != "text/html":
            return
        r.payload = self.strip.sub("", r.payload)
