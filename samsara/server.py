import sys
import os
import glob
import imp
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

def module_mtime(module):
    """Work out the mtime of a loaded module
    """
    file = module.__file__
    # Make sure we are looking at the .py file
    if os.path.exists(file[:-1]):
        file = file[:-1]
    return os.path.getmtime(file)

class SamsaraServer:
    """Serve pages
    """

    prefix = "samsara.handlers."

    def __init__(self, root):
        self.root = os.path.abspath(root)

        self.xmlctx = context.XMLContext(os.path.join(root, "XPath"))
        self.handlers = {}

    def __handlers(self):
        """Get a list of handlers, sorted by priority
        """
        samsara_dir = os.path.split(os.path.abspath(__file__))[0]
        sams_handlers = os.path.join(samsara_dir, "handlers")
        user_handlers = os.path.join(self.root, "Handlers")
        
        modules = filter(lambda n: n != "__init__",
                         map(lambda p: os.path.split(p)[1][:-3],
                             glob.glob(os.path.join(sams_handlers, "*.py")) +
                             glob.glob(os.path.join(user_handlers, "*.py"))))

        # Unload modules whose files have been deleted
        for name in self.handlers.keys():
            if name not in modules:
                del self.handlers[name]
                del sys.modules[self.prefix + name]

        # Load new modules and reload changed ones as necessary
        for name in modules:
            fullname = self.prefix + name

            if sys.modules.has_key(fullname):
                # Already loaded, reload if necessary
                old_mtime = sys.modules[fullname].__mtime__
                mtime = module_mtime(sys.modules[fullname])
            else:
                # Not yet loaded
                mtime, old_mtime = 0, -1

            if mtime > old_mtime:
                f, p, d = imp.find_module(name, [user_handlers, sams_handlers])
                try:
                    module = imp.load_module(fullname, f, p, d)

                    if mtime == 0:
                        mtime = module_mtime(module)
                    module.__mtime__ = mtime

                    # Create the handler
                    klass = getattr(module, name.capitalize() + "Handler")
                    self.handlers[name] = klass(self.root, self.xmlctx)

                finally:
                    if f:
                        f.close()

        # Return a sorted list of handlers
        handlers = map(lambda k: self.handlers[k], self.handlers.keys())
        handlers.sort(lambda a, b: b.priority - a.priority)
        return handlers

    def get(self, uri):
        """Serve a page
        """
        r = Request(uri)

        for h in self.__handlers():
            h.handle(r)

        if r.data is None:
            raise NotFoundError, "%s not found" % uri

        return r
