import os
from samsara import server
from samsara.xml import context as xmlctx
from samsara.util import guesstype

class FileHandler(server.HandlerClass):
    """Source static data from the filesystem
    """
    priority = -10

    def handle(self, r):
        if r.data or r.xml:
            return
        
        path = apply(os.path.join, [self.root] + r.uri.split("/"))
        if not os.path.isfile(path):
            return None

        r.type = guesstype.guessType(path)
        if r.type == "text/xml":
            r.xml = xmlctx.parseFile(path)
        else:
            if r.type == "application/x-sh":
                r.type = "text/plain"
            r.data = open(path, "r").read()
