import os
from samsara.server import SamsaraServer

def spider(root, dest, startpoints = "/", exclusions = ()):
    server = SamsaraServer(root)
    server.xmlctx.cache_stylesheets = True
    
    items = {}
    for path in startpoints:
        items[path] = False

    while True:
        todo = [path for path, done in items.items() if not done]
        if not todo:
            break

        for path in todo:
            items[path] = True
            response = server.get(path)
            server.auto_update = False
            server.xmlctx.xpathctx.auto_update = False

            links = [link.normalizeTo(path)
                     for link in response.links()
                     if link.isLocal()]

            for link in links:
                if not items.has_key(link):
                    for excl in exclusions:
                        if link[:len(excl)] == excl:
                            break
                    else:
                        items[link] = False

            if path[-1] == "/":
                payload = response.payload
                if isinstance(payload, str) and payload.find("<?php") != -1:
                    path += "index.php"
                else:
                    path += "index.html"
            path = os.path.join(dest, path[1:])
            dir = os.path.dirname(path)
            if not os.path.isdir(dir):
                os.makedirs(dir)
            response.writePayload(path)
