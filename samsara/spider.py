import os
import samsara.server
import sys
import traceback

class Worker:
    server = None
    
    def __init__(self, root, dest, accel = True):
        self.root = root
        self.dest = dest
        self.accel = accel

    def __call__(self, path):
        try:
            result = self.process(path)
            success = True
        except KeyboardInterrupt:
            return
        except:
            result = "".join(traceback.format_exception(*sys.exc_info()))
            success = False
        return success, result

    def process(self, path):
        if self.server is None:
            Worker.server = samsara.server.SamsaraServer(self.root)
            Worker.server.xmlctx.cache_stylesheets = True
            Worker.server.use_accelerators = self.accel

        response = self.server.get(path)
        for loader in (self.server, self.server.xmlctx.xpathctx):
            if loader.is_loaded:
                loader.auto_update = False

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

def spider(root, dest, startpoints = "/", exclusions = (), jobs = 1,
           accel = True):
    if jobs == 1:
        MAP = map
    else:
        import multiprocessing
        pool = multiprocessing.Pool(processes = jobs)
        MAP = lambda func, iterable: pool.map(func, iterable, 1)
    worker = Worker(root, dest, accel)

    items = {}
    for path in startpoints:
        items[path] = False

    while True:
        todo = [path for path, done in items.items() if not done]
        if not todo:
            break
        try:
            results = MAP(worker, todo)
        except KeyboardInterrupt:
            if jobs != 1:
                pool.terminate()
            sys.exit(1)
        for success, result in results:
            if not success:
                sys.stderr.write(result)
                sys.exit(1)
            for link in result:
                if not items.has_key(link):
                    for excl in exclusions:
                        if link[:len(excl)] == excl:
                            break
                        else:
                            items[link] = False
        for path in todo:
            items[path] = True

    if jobs == 1:
        del Worker.server
