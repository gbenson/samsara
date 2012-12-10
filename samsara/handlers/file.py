import os
from samsara import server
from samsara.util import guesstype

class FileHandler(server.HandlerClass):
    """Source static data from the filesystem
    """
    priority = -10

    def handle(self, r):
        if r.payload is not None:
            return
        
        path = apply(os.path.join, [self.root] + r.uri.split("/"))
        if not os.path.isfile(path):
            return None

        r.type = guesstype.guessType(path)
        if r.type == "text/xml":
            r.payload = self.xmlctx.parseFile(path)
        else:
            r.payload = server.File(path)
