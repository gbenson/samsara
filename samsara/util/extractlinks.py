import re
import posixpath
import urlparse
from samsara.xml import sax

def cssExtractLinks(css):
    """Extract URLs from some CSS

    Currently very very simplistic: it makes no attempt to properly
    parse the CSS, knows nothing of comments, and only recognises
    '@import' and 'url()' lines.

    The URLs are not guaranteed to be unique.
    """
    hrefs = []
    href_re = re.compile(r'@import\s+"([^"]*)";|url\(([^)]*)\)')
    for line in css.split("\n"):
        m = href_re.search(line)
        if m:
            hrefs.append(m.group(1) or m.group(2))
    return hrefs

class HTMLError(Exception):
    """There is an error in the supplied HTML
    """
    pass

xml_re = re.compile("^(<\?xml|<!DOCTYPE\s[^>]*XHTML)")

def htmlExtractLinks(html):
    """Extract URLs from some HTML (or XHTML)

    The URLs are not guaranteed to be unique.
    """
    class Parser(sax.SAXCallback):
        def __init__(self, type):
            self.type = type
            self.style = None
            self.base = None
            self.hrefs = []

        def addHref(self, href):
            if self.base:
                # XXX: written with no reference to any spec, hence
                # very, very suspect, but it seems to work ;)
                bits = urlparse.urlparse(href)
                if bits[:2] == ("", ""):
                    path = posixpath.join(self.base[2], bits[2])
                    href = urlparse.urlunparse(self.base[:2]
                                               + (path,)
                                               + bits[3:])
            self.hrefs.append(href)

        def startElement(self, tag, attrs):
            if self.style is not None:
                raise HTMLError, "<%s> within <style>" % tag
            if attrs is None:
                attrs = {}

            if tag == "base" and attrs.has_key("href"):
                scheme, netloc, path = urlparse.urlparse(attrs["href"])[:3]
                path = posixpath.split(path)[0]
                self.base = scheme, netloc, path
            elif tag == "a" and attrs.has_key("href"):
                self.addHref(attrs["href"])
            elif tag == "img":
                self.addHref(attrs["src"])
            elif tag == "link" and attrs.has_key("href"):
                self.addHref(attrs["href"])
            elif tag == "script" and attrs.has_key("src"):
                self.addHref(attrs["src"])
            elif (tag == "style"
                  and attrs.has_key("type")
                  and attrs["type"] == "text/css"):
                self.style = ""

        def endElement(self, tag):
            if tag == "style" and self.style is not None:
                for href in cssExtractLinks(self.style):
                    self.addHref(href)
                self.style = None
            elif self.style is not None:
                raise HTMLError, "</%s> within <style>" % tag

        def characters(self, data):
            if self.style is not None:
                self.style += data

        def error(self, msg):
            # HTML is allowed to be broken
            if self.type != "HTML":
                sax.SAXCallback.error(self, msg)

    if xml_re.match(html):
        return sax.parseXML(html, Parser("XML")).hrefs
    else:
        return sax.parseHTML(html, Parser("HTML")).hrefs
