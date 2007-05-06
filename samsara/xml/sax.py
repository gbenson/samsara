import libxml2
import cStringIO as StringIO

class SAXError(Exception):
    """There is an error in the supplied XML
    """
    pass

class SAXCallback:
    """Base class for SAX handlers
    """
    def warning(self, msg):
        raise SAXError, msg

    def error(self, msg):
        raise SAXError, msg

    def fatalError(self, msg):
        raise SAXError, msg

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
                parseChunk = libxml2.parserCtxt.htmlParseChunk
            else:
                raise RuntimeError, "unknown document type '%s'" % what
            
        else:
            parseChunk(ctxt, chunk, len(chunk), 0)

    if ctxt:
        parseChunk(ctxt, "", 0, 1)

    return handler

def parseXML(mem, handler, uri="<RAM>"):
    """Parse a block of memory as XML using SAX
    """
    return __parseFileObject(StringIO.StringIO(mem), handler, uri, "XML")

def parseHTML(mem, handler, uri="<RAM>"):
    """Parse a block of memory as HTML using SAX
    """
    return __parseFileObject(StringIO.StringIO(mem), handler, uri, "HTML")
