import sys
import os
import glob
import imp
import types
import libxml2
import libxslt
from samsara.util import intercept

# libxml2 and libxslt print loads of crap to stdout and stderr when
# things go wrong.  We intecept this and turn it into exceptions.
STREAMS = intercept.STDOUT | intercept.STDERR

class XMLError(Exception):
    """There is an error in the supplied XML
    """
    pass

class XMLContext:
    """A manipulator of XML data
    """
    def __init__(self, xpathdir = None):
        self.xpathctx = XPathContext(xpathdir)

    def parseFile(self, path):
        """Parse an XML file and build a tree
        """
        doc, errors = intercept.intercept(STREAMS, libxml2.parseFile, path)
        if doc is None or errors:
            raise XMLError, errors + "error: can't load %s" % path
        return doc

    def __parseXSLFile(self, path):
        """Parse an XSLT stylesheet building the associated structures
        """
        doc = self.parseFile(path)
        style, errors = intercept.intercept(STREAMS,
                                            libxslt.parseStylesheetDoc, doc)
        if style is None or errors:
            raise XMLError, errors + "error: can't load %s" % path
        return style

    def __applyStylesheet(self, doc, style, params):
        """The core of applyStylesheet and applyStylesheetPI
        """
        params = params.copy()
        for param in params.keys():
            if (type(params[param]) != types.InstanceType or
                not isinstance(params[param], libxml2.xmlNode)):
                params[param] = "'" + str(params[param]) + "'"

        self.xpathctx.install()
        try:
            result, errors = intercept.intercept(
                STREAMS, style.applyStylesheet, doc, params)
        finally:
            self.xpathctx.remove()

        if result is None or errors:
            raise XMLError, errors + "error: can't apply stylesheet"
        return result

    def applyStylesheet(self, doc, path, params = {}):
        """Apply an XSLT stylesheet to a document.
        """
        style = self.__parseXSLFile(path)

        try:
            return self.__applyStylesheet(doc, style, params)
        finally:
            style.freeStylesheet()

    def applyStylesheetPI(self, doc, params = {}):
        """Apply an XSLT stylesheet (referenced in a PI) to a document.
        """
        style, errors = intercept.intercept(STREAMS,
                                            libxslt.loadStylesheetPI, doc)
        if style is None or errors:
            raise XMLError, errors + "error: can't load stylesheet"

        try:
            return self.__applyStylesheet(doc, style, params)
        finally:
            style.freeStylesheet()

def module_mtime(module):
    """Work out the mtime of a loaded module
    """
    file = module.__file__
    # Make sure we are looking at the .py file
    if os.path.exists(file[:-1]):
        file = file[:-1]
    return os.path.getmtime(file)

class XPathContext:
    """Handle XPath extension functions

    This directly affects sys.modules and cannot be recoded so it does
    not.  If you want to have more than one XPathContext object for
    different directories then you'd need to ensure that the prefixes
    for each didn't collide.

    Since this is the case, I've taken liberties by keeping the
    functions registered all the time.  In reality, they ought to be
    registered at the end of install() and unregistered by remove().

    Actually, libxslt.registerExtModuleFunction won't register a
    function that has previously been unregistered, and there seems to
    be no way to unload a function.  Sigh.  We work around this rather
    than try to fix libxslt since libxslt is _hairy_.
    """

    namespace = "http://inauspicious.org/samsara"
    prefix = "samsara.xml.xpath."

    def __init__(self, dir):
        self.dir = dir
        self.names = []
        self.registered = []

    def install(self):
        if not self.dir:
            return

        modules = map(lambda p: os.path.split(p)[1][:-3],
                      glob.glob(os.path.join(self.dir, "*.py")))

        # Unload modules whose files have been deleted
        for name in self.names:
            if name not in modules:
                del sys.modules[self.prefix + name]
        self.names = modules

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
                f, p, d = imp.find_module(name, [self.dir])
                try:
                    module = imp.load_module(fullname, f, p, d)

                    if mtime == 0:
                        mtime = module_mtime(module)
                    module.__mtime__ = mtime

                    # Register the function
                    if name not in self.registered:
                        libxslt.registerExtModuleFunction(
                            name, self.namespace, self.Function(self, name))
                        self.registered.append(name)

                finally:
                    if f:
                        f.close()

    def remove(self):
        pass

    class Function:
        """Object used to hack around the aforementioned libxslt breakage
        """
        def __init__(self, xmlctx, name):
            self.xmlctx = xmlctx
            self.name = name

        def __call__(self, *args):
            if self.name not in self.xmlctx.names:
                # Mimic what happens when a real unregistered function
                # is called (albeit imperfectly)
                print >>sys.stderr, "xmlXPathCompOpEval: function", \
                      self.name, " not found"
                print >>sys.stderr, "Error Unregistered function"
                return None
            module = sys.modules[self.xmlctx.prefix + self.name]
            func = getattr(module, self.name)
            return apply(func, args)
