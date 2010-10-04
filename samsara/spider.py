import os

def spider(server, dest, startpoints, exclusions = ()):
    items = {}
    for path in startpoints:
        items[path] = 0

    while 1:
        todo = filter(lambda i: not items[i], items.keys())
        if not todo:
            break

        for path in todo:
            items[path] = 1
            response = server.get(path)

            links = map(lambda l: l.normalizeTo(path),
                        filter(lambda l: l.isLocal(),
                               response.links()))
            for link in links:
                if not items.has_key(link):
                    for excl in exclusions:
                        if link[:len(excl)] == excl:
                            break
                    else:
                        items[link] = 0

            if path[-1] == "/":
                payload = response.payload
                if isinstance(payload, str) and payload.find("<?php") != -1:
                    path += "index.php"
                else:
                    path += "index.html"
            path = os.path.join(dest, path[1:])
            dir = os.path.split(path)[0]
            if not os.path.isdir(dir):
                os.makedirs(dir)
            response.writePayload(path)
