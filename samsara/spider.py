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
                path += "index.html"
            if hasattr(response, "filename"):
                path = os.path.join(os.path.split(path)[0], response.filename)
            path = os.path.join(dest, path[1:])
            dir = os.path.split(path)[0]
            if not os.path.isdir(dir):
                os.makedirs(dir)
            open(path, "w").write(response.data)
