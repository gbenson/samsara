import os
import re
from samsara import server
from samsara.util import xml

diary_match_re = re.compile(r"^diary/(\d{4})/(\d{2})/(\d{2})/$")

class DiaryHandler(server.HandlerClass):
    """Generate diary pages
    """
    def __init__(self, root):
        server.HandlerClass.__init__(self, root)

        self.diary   = os.path.join(self.root, "DB/diary/diary.xml")
        self.day_xsl = os.path.join(self.root, "DB/diary/day.xsl")

    def handle(self, r):
        m = diary_match_re.search(r.uri)
        if not m:
            return

        # Work out what to serve
        params = {"year":  m.group(1),
                  "month": m.group(2),
                  "day":   m.group(3)}
        style = self.day_xsl

        # Render the page
        db = xml.parseFile(self.diary)
        try:
            doc = xml.applyStylesheet(db, style, params)
            doc.setBase(os.path.join(self.root, r.uri, "index.xml"))

        finally:
            db.freeDoc()

        # Add it to the request
        r.type = "text/xml"
        r.xml = doc
