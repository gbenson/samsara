import ConfigParser
import hashlib
import sys
import os
import urlparse
import posixpath
import operator
import types
import weakref
from samsara.util import extractlinks
from samsara.util import loader
from samsara.xml import context

class NotFoundError(Exception):
    pass

class HandlerClass:
    """Base class for all Samsara handlers
    """
    priority = 0

    def __init__(self, server):
        self.__server = server
        self.docs = {}

    def __del__(self):
        if hasattr(self, "docs"):
            for doc, old_mtime, name, callback in self.docs.values():
                if doc is not None:
                    doc.freeDoc()

    @property
    def server(self):
        return self.__server()

    @property
    def root(self):
        return self.server.root

    @property
    def xmlctx(self):
        return self.server.xmlctx

    def get_handler(self, name):
        [handler] = self.server.handlers[name]
        assert self.priority < handler.priority
        return handler

    def registerDocument(self, path, name = None, callback = None):
        """Register an XML document to maintain a cached copy of.
        """
        assert not self.docs.has_key(path)
        self.docs[path] = (None, 0, name, callback)

    def updateDocuments(self):
        """Ensure all registered documents are up to date.
        """
        for path in self.docs.keys():
            self.__updateDocument(path)

    def __updateDocument(self, path):
        doc, old_mtime, name, callback = self.docs[path]
        mtime = os.path.getmtime(path)
        if mtime == old_mtime:
            return
        if doc is not None:
            del self.docs[path]
            doc.freeDoc()
        self.docs[path] = (None, 0, name, callback)
        doc = self.xmlctx.parseFile(path)
        if name is not None:
            setattr(self, name, doc)
        self.docs[path] = (doc, mtime, name, callback)
        if callback is not None:
            callback(doc)

    def __str__(self):
        return "%4d %s" % (self.priority, repr(self))

class File:
    """A request payload that has not yet been read from disk
    """
    def __init__(self, path):
        self.path = path

class Request:
    """Samsara request, the argument to all handler handle methods
    """
    def __init__(self, uri):
        if not uri or uri[0] != "/":
            raise ValueError, "URI must begin with a slash"
        self.uri = uri[1:]

        self.type = None
        self.payload = None
        self.implied = []
        self.buttons = []

    def __del__(self):
        if hasattr(self, "type") and self.type == "text/xml":
            self.payload.freeDoc()

    def addButton(self, text, href, position=None):
        button = text, href
        if position is None:
            self.buttons.append(button)
        else:
            self.buttons.insert(0, button)

    class Redirect(Exception):
        pass

    def redirect(self, uri):
        assert self.payload is None
        raise self.Redirect("/" + uri)

    def getPayload(self):
        if isinstance(self.payload, File):
            self.payload = open(self.payload.path, "r").read()
        return self.payload

    def writePayload(self, path):
        if isinstance(self.payload, File):
            try:
                os.link(self.payload.path, path)
                return
            except OSError:
                pass
        open(path, "w").write(self.getPayload())

    def add_implied(self, link):
        """Allow the existence of one page to imply the existence of
        others to the spiderer.
        """
        self.implied.append("/" + link)

    def links(self):
        """Extract all URLs from the response's body
        """
        if self.type == "text/css":
            links = extractlinks.cssExtractLinks(self.getPayload())
        elif self.type == "text/html":
            links = extractlinks.htmlExtractLinks(self.getPayload())
        else:
            links = []
        links.extend(self.implied)
        return map(Link, links)

class Link:
    """URL returned by Request.links()
    """

    def __init__(self, url):
        self.url = url
        (self.scheme, self.netloc, self.path, self.params,
         self.query, self.fragment) = urlparse.urlparse(url)

    def isLocal(self):
        """Is the link local to the site?
        """
        return (self.scheme, self.netloc) == ("", "")

    def normalizeTo(self, base):
        """Return an absolute URL, relative to the site.

        Will choke on non-local URLs, and those with either parameters
        or a query string. The fragment, if any, is removed.
        """
        assert self.isLocal()

        path = posixpath.join(posixpath.split(base)[0], self.path)
        slash = ["", "/"][path != "/" and path[-1] == "/"]
        return posixpath.normpath(path) + slash

class SamsaraConfigParser(ConfigParser.ConfigParser):
    """Configuration file parser
    """

    def set_default(self, section, option, value):
        if self.has_option(section, option):
            return
        if not self.has_section(section):
            self.add_section(section)
        self.set(section, option, str(value))

class SamsaraServer(loader.Loader):
    """Serve pages
    """

    def __init__(self, root):
        self.root = os.path.realpath(root)
        assert os.path.isdir(self.root)
        self.data = os.path.join(os.environ["HOME"],
                                 ".samsara",
                                 hashlib.md5(self.root).hexdigest()[:8])
        for caps in (True, False):
            usercode = "samsara"
            if caps:
                usercode = usercode.title()
            usercode = os.path.join(root, usercode)
            if os.path.isdir(usercode):
                break

        self.config = SamsaraConfigParser()
        inipath = os.path.join(usercode, "samsara.ini")
        if os.path.exists(inipath):
            self.config.read(inipath)
        self.config.set_default("httpserver", "port", 2420)

        common_dir = os.path.join(usercode, "common")
        if common_dir not in sys.path:
            sys.path.insert(0, common_dir)

        self.xmlctx = context.XMLContext(os.path.join(usercode, "xpath"))

        samsara_dir = os.path.split(os.path.abspath(__file__))[0]
        sams_handlers = os.path.join(samsara_dir, "handlers")
        user_handlers = os.path.join(usercode, "handlers")
        loader.Loader.__init__(
            self, [user_handlers, sams_handlers], "samsara.handlers")
        self.handlers = {}

        self.weakref = weakref.ref(self)

        self.httpserver = None
        self.use_accelerators = True

    def setHTTPServer(self, httpserver):
        if httpserver is None:
            self.__httpserver = None
        else:
            self.__httpserver = weakref.ref(httpserver)

    def getHTTPServer(self):
        if self.__httpserver is not None:
            return self.__httpserver()

    httpserver = property(getHTTPServer, setHTTPServer)

    def datadir(self, type, path):
        assert type in ("cache", "config")
        assert not os.sep in path
        return os.path.join(self.data, type, path)

    def moduleLoaded(self, name, module):
        """Callback called when a module is (re)loaded
        """
        self.handlers[name] = [
            item(self.weakref)
            for item in [getattr(module, attr)
                         for attr in dir(module)
                         if not attr.startswith("_")]
            if type(item) == types.ClassType
               and issubclass(item, HandlerClass)]

    def moduleUnloaded(self, name):
        """Callback called when a module is unloaded
        """
        del self.handlers[name]

    def get(self, uri):
        """Serve a page
        """
        self.updateCache()
        handlers = reduce(operator.add, self.handlers.values())
        handlers.sort(lambda a, b: b.priority - a.priority)
        if self.auto_update:
            for handler in handlers:
                handler.updateDocuments()

        uris = {}
        while True:
            if uris.has_key(uri):
                raise NotFoundError, "circular redirect"
            uris[uri] = True

            r = Request(uri)

            if self.httpserver is None and self.use_accelerators:
                accelerators = {}
                for handler in handlers:
                    accel = getattr(handler, "accelerator", None)
                    if accel is not None:
                        accelerators[accel] = True
                for accel in accelerators:
                    [accel] = self.handlers[accel]
                    if accel.accelerate(r):
                        return r

            try:
                for handler in handlers:
                    handler.handle(r)
            except Request.Redirect, e:
                uri = str(e)
                continue
            break

        if r.payload is None:
            raise NotFoundError, "%s not found" % uri

        return r
