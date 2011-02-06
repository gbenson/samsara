import multiprocessing
import operator
import os
import samsara.server
import sys

class Worker:
    server = None
    
    def __init__(self, root, dest):
        self.root = root
        self.dest = dest

    def __call__(self, path):
        if self.server is None:
            Worker.server = samsara.server.SamsaraServer(self.root)
            Worker.server.xmlctx.cache_stylesheets = True

        response = self.server.get(path)
        self.server.auto_update = False
        self.server.xmlctx.xpathctx.auto_update = False

        links = [link.normalizeTo(path)
                 for link in response.links()
                 if link.isLocal()]

        if path[-1] == "/":
            payload = response.payload
            if isinstance(payload, str) and payload.find("<?php") != -1:
                path += "index.php"
            else:
                path += "index.html"
        path = os.path.join(self.dest, path[1:])
        dir = os.path.dirname(path)
        try:
            os.makedirs(dir)
        except:
            pass
        response.writePayload(path)

        return links

def spider(root, dest, startpoints = "/", exclusions = ()):
    pool = multiprocessing.Pool(processes = 3)
    worker = Worker(root, dest)

    items = {}
    for path in startpoints:
        items[path] = False

    while True:
        todo = [path for path, done in items.items() if not done]
        if not todo:
            break
        for link in reduce(operator.add, pool.map(worker, todo, 1)):
            if not items.has_key(link):
                for excl in exclusions:
                    if link[:len(excl)] == excl:
                        break
                    else:
                        items[link] = False
        for path in todo:
            items[path] = True
