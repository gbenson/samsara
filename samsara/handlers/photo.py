import os
import re
from samsara import server
from samsara.util import xml

photo_match_re = re.compile(r"^photos/films/((\d{3})/((\d{2})/)?)?$")

class PhotoHandler(server.HandlerClass):
    """Generate indexes of directories in the photos subtree
    """
    def __init__(self, root):
        server.HandlerClass.__init__(self, root)

        self.photodb   = os.path.join(self.root, "DB/photos/photos.xml")
        self.index_xsl = os.path.join(self.root, "DB/photos/index.xsl")
        self.photo_xsl = os.path.join(self.root, "DB/photos/photo.xsl")

    def handle(self, r):
        m = photo_match_re.search(r.uri)
        if not m:
            return

        # Work out what to serve
        film, photo = m.group(2), m.group(4)
        if photo:
            style = self.photo_xsl
            params = {"film":  film, "photo": photo}
        elif film:
            style = self.index_xsl
            params = {"film":  film}
        else:
            style = self.index_xsl
            params = {}

        # Render the page
        db = xml.parseFile(self.photodb)
        try:
            doc = xml.applyStylesheet(db, style, params)
            doc.setBase(os.path.join(self.root, r.uri, "index.xml"))

        finally:
            db.freeDoc()

        # Add it to the request
        r.type = "text/xml"
        r.xml = doc
