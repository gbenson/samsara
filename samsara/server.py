import os
import glob
import urlparse
import posixpath
from samsara.util import extractlinks
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

class SamsaraServer:
    """Serve pages
    """
    def __init__(self, root):
        self.root = os.path.abspath(root)

        handlers = map(self.__importHandler, self.__listHandlers())
        handlers.sort(lambda a, b: b.priority - a.priority)
        self.handlers = map(lambda s: s(self.root, context), handlers)

    def __listHandlers(self):
        """Return a list of handler modules
        """
        samsara_dir = os.path.split(os.path.abspath(__file__))[0]
        return filter(lambda n: n != "__init__",
                      map(lambda p: os.path.split(p)[1][:-3],
                          glob.glob(os.path.join(samsara_dir,
                                                 "handlers", "*.py"))))

    def __importHandler(self, name):
        """Extract the handler class from a Samsara handler module
        """
        module = __import__("samsara.handlers." + name)
        module = getattr(module, "handlers")
        module = getattr(module, name)
        handler = name.capitalize() + "Handler"
        if hasattr(module, handler):
            return getattr(module, handler)

    def get(self, uri):
        """Serve a page
        """
        r = Request(uri)

        for h in self.handlers:
            h.handle(r)

        if r.data is None:
            raise NotFoundError, "%s not found" % uri

        return r
