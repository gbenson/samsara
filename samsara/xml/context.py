import types
import libxml2
import libxslt
from samsara.util import intercept
from samsara import xpathext

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

        result, errors = intercept.intercept(STREAMS,
                                             style.applyStylesheet,
                                             doc, params)
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

# XPath extension functions

namespace = "http://inauspicious.org/samsara"

for f in filter(lambda i: type(getattr(xpathext, i)) == types.FunctionType,
                filter(lambda i: i[:2] != "__", dir(xpathext))):
    libxslt.registerExtModuleFunction(f, namespace, getattr(xpathext, f))
