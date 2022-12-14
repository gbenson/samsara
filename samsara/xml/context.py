import os
import sys
import types
import libxml2
import libxslt
from samsara.util import intercept
from samsara.util import loader

# libxml2 and libxslt print loads of crap to stdout and stderr when
# things go wrong.  We intecept this and turn it into exceptions.
STREAMS = intercept.STDOUT | intercept.STDERR

class XMLError(Exception):
    """There is an error in the supplied XML
    """
    pass

class Stylesheet:
    """A stylesheet
    """
    def __init__(self, xmlctx, path):
        self.doc = xmlctx.parseFile(path)
        self.style, errors = intercept.intercept(
            STREAMS, libxslt.parseStylesheetDoc, self.doc)
        if self.style is None or errors:
            raise XMLError, errors + "error: can't load %s" % path

    def __del__(self):
        if hasattr(self, "style") and self.style is not None:
            self.style.freeStylesheet()
        elif hasattr(self, "doc") and self.doc is not None:
            self.doc.freeDoc()

    def applyStylesheet(self, *args, **kwargs):
        return self.style.applyStylesheet(*args, **kwargs)

class XMLContext:
    """A manipulator of XML data
    """
    def __init__(self, xpathdir = None):
        self.xpathctx = XPathContext(xpathdir)
        self.validctx = libxml2.newValidCtxt()
        self.cache_stylesheets = False
        self.__xslcache = {}

    def __validate(self, doc, path = ""):
        """Validate an XML file
        """
        if hasattr(doc, "samsara_validated"):
            return
        junk, errors = intercept.intercept(STREAMS,
                                           doc.validateDocument, self.validctx)
        if errors and errors != "no DTD found!\n":
            doc.freeDoc()
            raise XMLError, errors
        doc.samsara_validated = True

    def parseFile(self, path):
        """Parse an XML file and build a tree
        """
        saved = libxml2.substituteEntitiesDefault(True)
        try:
            doc, errors = intercept.intercept(STREAMS, libxml2.parseFile, path)
        finally:
            libxml2.substituteEntitiesDefault(saved)
        if doc is None or errors:
            raise XMLError, errors + "error: can't load %s" % path
        self.__validate(doc)
        return doc

    def getStylesheet(self, path):
        path = os.path.realpath(path)
        if self.cache_stylesheets and self.__xslcache.has_key(path):
            return self.__xslcache[path]
        style = Stylesheet(self, path)
        if self.cache_stylesheets:
            self.__xslcache[path] = style
        return style
    
    def applyStylesheet(self, doc, path, params = {}):
        """Apply an XSLT stylesheet to a document.
        """
        self.__validate(doc)
        style = self.getStylesheet(path)

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

    def copyNode(self, src, dst):
        if src.type == "element":
            dst = dst.newChild(None, src.name, None)
            node = src.properties
            while node:
                dst.setProp(node.name, node.content)
                node = node.next
            node = src.children
            while node:
                self.copyNode(node, dst)
                node = node.next
        elif src.type == "text":
            dst.addContent(src.content)
        else:
            raise XMLError, "unhandled node type '%s'" % src.type

class XPathContext(loader.Loader):
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

    def __init__(self, dir):
        self.disabled = not dir
        if self.disabled:
            return

        loader.Loader.__init__(self, [dir], "samsara.xpath")
        self.registered = []

    def install(self):
        if self.disabled:
            return
        self.updateCache()

    def remove(self):
        pass

    def moduleLoaded(self, name, module):
        """Callback called when a module is (re)loaded
        """
        if name not in self.registered:
            libxslt.registerExtModuleFunction(
                name, self.namespace, self.Function(self, name))
            self.registered.append(name)

    class Function:
        """Object used to hack around the aforementioned libxslt breakage
        """
        def __init__(self, xmlctx, name):
            self.xmlctx = xmlctx
            self.name = name

        def __call__(self, *args):
            # Get the function
            if self.name not in self.xmlctx.names:
                # Mimic what happens when a real unregistered function
                # is called (albeit imperfectly)
                print >>sys.stderr, "xmlXPathCompOpEval: function", \
                      self.name, " not found"
                print >>sys.stderr, "Error Unregistered function"
                return None
            module = sys.modules[self.xmlctx.prefix + self.name]
            func = getattr(module, self.name)

            # Wrap the arguments where necessary
            ctx, nodesets = args[0], args[1:]
            ctx = libxslt.xpathParserContext(_obj=ctx)
            nodesets = map(self.__wrap_nodeset, nodesets)
            
            # Go go go
            return apply(func, [ctx] + nodesets)

        def __wrap_nodeset(self, nodeset):
            if isinstance(nodeset, str):
                return nodeset
            return [libxml2.xmlNode(_obj = node) for node in nodeset]
