import types
import libxml2
import libxslt
import cStringIO as StringIO
from samsara.util import intercept
from samsara import xpathext

# libxml2 and libxslt print loads of crap to stdout and stderr when
# things go wrong.  We intecept this and turn it into exceptions.
STREAMS = intercept.STDOUT | intercept.STDERR

class XMLError(Exception):
    """There is an error in the supplied XML
    """
    pass

# Function to parse XML and build a DOM tree

def parseFile(path):
    """Parse an XML file and build a tree
    """
    doc, errors = intercept.intercept(STREAMS, libxml2.parseFile, path)
    if doc is None or errors:
        raise XMLError, errors + "error: can't load %s" % path
    return doc

# Functions to apply XSLT stylesheets to DOM trees

def __parseXSLFile(path):
    """Parse an XSLT stylesheet building the associated structures
    """
    doc = parseFile(path)
    style, errors = intercept.intercept(STREAMS,
                                        libxslt.parseStylesheetDoc, doc)
    if style is None or errors:
        raise XMLError, errors + "error: can't load %s" % path
    return style

def __applyStylesheet(doc, style, params):
    """The core of applyStylesheet and applyStylesheetPI
    """
    params = params.copy()
    for param in params.keys():
        if (type(params[param]) != types.InstanceType or
            not isinstance(params[param], libxml2.xmlNode)):
            params[param] = "'" + str(params[param]) + "'"

    result, errors = intercept.intercept(STREAMS,
                                         style.applyStylesheet, doc, params)
    if result is None or errors:
        raise XMLError, errors + "error: can't apply stylesheet"
    return result

def applyStylesheet(doc, path, params = {}):
    """Apply an XSLT stylesheet to a document.
    """
    style = __parseXSLFile(path)

    try:
        return __applyStylesheet(doc, style, params)
    finally:
        style.freeStylesheet()

def applyStylesheetPI(doc, params = {}):
    """Apply an XSLT stylesheet (referenced in a PI) to a document.
    """
    style, errors = intercept.intercept(STREAMS, libxslt.loadStylesheetPI, doc)
    if style is None or errors:
        raise XMLError, errors + "error: can't load stylesheet"

    try:
        return __applyStylesheet(doc, style, params)
    finally:
        style.freeStylesheet()

# XPath extension functions

namespace = "http://inauspicious.org/samsara"

for f in filter(lambda i: type(getattr(xpathext, i)) == types.FunctionType,
                filter(lambda i: i[:2] != "__", dir(xpathext))):
    libxslt.registerExtModuleFunction(f, namespace, getattr(xpathext, f))

# Functions to parse XML using SAX

class SAXCallback:
    """Base class for SAX handlers
    """
    def warning(self, msg):
        raise XMLError, msg

    def error(self, msg):
        raise XMLError, msg

    def fatalError(self, msg):
        raise XMLError, msg

chunksize = 1024

def __parseFileObject(file, handler, path, what):
    """Parse a file or file-like object using SAX
    """
    ctxt = None

    while 1:
        chunk = file.read(chunksize)
        if len(chunk) == 0:
            break

        if not ctxt:
            if what == "XML":
                ctxt = libxml2.createPushParser(handler, chunk,
                                                len(chunk), path)
                parseChunk = libxml2.parserCtxt.parseChunk
            elif what == "HTML":
                ctxt = libxml2.htmlCreatePushParser(handler, chunk,
                                                    len(chunk), path)
                parseChunk = libxml2.htmlParseChunk
            else:
                raise RuntimeError, "unknown document type '%s'" % what
            
        else:
            parseChunk(ctxt, chunk, len(chunk), 0)

    if ctxt:
        parseChunk(ctxt, "", 0, 1)

    return handler

def saxParseXML(mem, handler, uri="<RAM>"):
    """Parse a block of memory as XML using SAX
    """
    return __parseFileObject(StringIO.StringIO(mem), handler, uri, "XML")

def saxParseHTML(mem, handler, uri="<RAM>"):
    """Parse a block of memory as HTML using SAX
    """
    return __parseFileObject(StringIO.StringIO(mem), handler, uri, "HTML")
