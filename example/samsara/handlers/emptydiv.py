import re
import samsara.server

# IE6 and older don't respect declared dimensions and instead
# expand elements to fit their content.  They also don't recognise
# empty elements unless you comment out their non-existing content.
#   http://archivist.incutio.com/viewlist/css-discuss/87916

class EmptyDivFixer(samsara.server.HandlerClass):
    priority = -100
    find = re.compile("<div([^>]*)></div>")
    replace = r"<div\1><!-- --></div>"

    def handle(self, r):
        if r.type != "text/html":
            return
        r.payload = self.find.sub(self.replace, r.payload)
