from samsara import server
from samsara.util import curlyquote

class CurlyQuoter(server.HandlerClass):
    priority = -90

    def handle(self, r):
        if r.payload is None:
            # Don't try and process non-existing URLs
            return
        if isinstance(r.payload, server.File):
            # Don't touch anything we're spooling from the disk
            return
        if r.payload.rstrip()[-6:].lower() not in ("/html>", "</rss>"):
            # Only process HTML and RSS
            return
        r.payload = curlyquote.curlyquote(
            r.payload.decode("utf-8")).encode("utf-8")
