import sys
import os
import urlparse
import posixpath
from samsara.util import extractlinks
from samsara.util import loader
from samsara.xml import context

class NotFoundError(Exception):
    pass

class HandlerClass:
    """Base class for all Samsara handlers
    """
    priority = 0

    def __init__(self, root, xmlctx):
        self.root = root
        self.xmlctx = xmlctx

class Request:
    """Samsara request, the argument to all handler handle methods
    """
    def __init__(self, uri):
        if not uri or uri[0] != "/":
            raise ValueError, "URI must begin with a slash"        
        self.uri = uri[1:]

        self.type = None
        self.data = None
        self.xml  = None

    def __del__(self):
        if hasattr(self, "xml") and self.xml:
            self.xml.freeDoc()

    def links(self):
        """Extract all URLs from the response's body
        """
        if self.type == "text/css":
            links = extractlinks.cssExtractLinks(self.data)
        elif self.type == "text/html":
            links = extractlinks.htmlExtractLinks(self.data)
        else:
            links = []
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

class SamsaraServer(loader.Loader):
    """Serve pages
    """

    def __init__(self, root):
        self.root = os.path.abspath(root)
        usercode = os.path.join(root, "Samsara")

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

    def moduleLoaded(self, name, module):
        """Callback called when a module is (re)loaded
        """
        klass = getattr(module, name.capitalize() + "Handler")
        self.handlers[name] = klass(self.root, self.xmlctx)
        
    def moduleUnloaded(self, name):
        """Callback called when a module is unloaded
        """
        del self.handlers[name]

    def get(self, uri):
        """Serve a page
        """
        r = Request(uri)

        self.updateCache()
        handlers = map(lambda k: self.handlers[k], self.handlers.keys())
        handlers.sort(lambda a, b: b.priority - a.priority)
        for h in handlers:
            h.handle(r)

        if r.data is None:
            raise NotFoundError, "%s not found" % uri

        return r
