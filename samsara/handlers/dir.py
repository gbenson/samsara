import os
import time
import libxml2
from samsara import server
from samsara.util import xml
from samsara.util import guesstype
from samsara.util import date


# Modified versions of directory listing functions

def listdir(path):
    """Return a list containing the names of the entries in the directory

    Identical to os.listdir except that it ignores some files.
    """
    return filter(lambda entry: (entry != "CVS" and
                                 entry != "HEADER.html" and
                                 entry[0] != "." and
                                 entry[0] != "#" and
                                 entry[-1] != "~"), os.listdir(path))

def getmtime(path):
    """Return the last modification time of a file

    Identical to os.path.getmtime except that the mtime of a non-empty
    directory is defined as the mtime of the newest entry inside it.
    """
    if not os.path.isdir(path):
        return os.path.getmtime(path)

    times = map(getmtime, map(lambda e: os.path.join(path, e), listdir(path)))
    if not times:
        return os.path.getmtime(path)

    times.sort()
    return times[-1]


# Functions to create the directory listing

def createDirent(path):
    """Accumulate some information about an item in a directory
    """
    entry = os.path.split(path)[1]
    if os.path.isdir(path):
        return {"name": entry + "/",
                "date": getmtime(path),
                "type": "directory"}
    else:
        return {"name": entry,
                "date": getmtime(path),
                "size": os.path.getsize(path),
                "type": guesstype.guessBaseType(entry)}

def funkySortOrder(a, b):
    """Directories before files, then newest first, then alphabetical.
    """
    if a["type"] == "directory" and b["type"] != "directory":
        return -1
    if a["type"] != "directory" and b["type"] == "directory":
        return 1
    if a["date"] > b["date"]:
        return -1
    if a["date"] < b["date"]:
        return 1
    if a["name"] < b["name"]:
        return -1
    if a["name"] > b["name"]:
        return 1

def prettifyDirent(entry):
    """Prettify a directory entry created by createDirent
    """
    entry = entry.copy()

    entry["date"] = date.strftime("%o %B %Y", time.localtime(entry["date"]))

    if entry.has_key("size"):
        size = entry["size"]
        if size < 1024:
            entry["size"] = "%db" % size
        elif size < 1048576:
            entry["size"] = "%.1fk" % (size/1024.0)
        else:
            entry["size"] = "%.1fM" % (size/1048576.0)

    if not entry["type"]:
        entry["type"] = "text/plain"

    entry["icon"] = {"directory":              "folder",
                     "application/postscript": "ps",
                     "application/pdf":        "pdf",
                     "application/x-sh":       "script",
                     "application/x-tar":      "compressed",
                     "application/zip":        "compressed",
                     "image/jpeg":             "image2",
                     "image/png":              "image2",
                     "text/plain":             "text"
                     }.get(entry["type"], "generic")
    return entry


# The handler class itself

class DirHandler(server.HandlerClass):
    """Generate directory indexes
    """
    priority = -5

    def handle(self, r):
        if r.data or r.xml:
            return
        
        path = apply(os.path.join, [self.root] + r.uri.split("/"))
        if path[-1] != "/":
            return
        path = path[:-1]
        if not os.path.isdir(path):
            return

        # If we find a static index, we rewrite the request and let
        # the file handler serve it in our stead.
        for index in "index.xml", "index.html":
            newpath = os.path.join(path, index)
            if os.path.isfile(newpath):
                r.uri = newpath[len(self.root) + 1:]
                return

        # Create the directory index
        contents = map(lambda e: createDirent(os.path.join(path, e)),
                       listdir(path))
        contents.sort(funkySortOrder)
        contents = map(prettifyDirent, contents)

        # Render the page
        uri = path[len(self.root)+1:]

        if uri:
            stylepath = len(uri.split("/")) * "../" + "style"
            absolute = "/" + uri + "/"
        else:
            stylepath = "style"
            absolute = "/"

        doc = libxml2.newDoc("1.0")
        doc.setBase(os.path.join(path, "index.xml"))
        doc.addChild(libxml2.newPI("xml-stylesheet",
                                   'href="%s/index.xsl" type="text/xsl"' % \
                                   stylepath))
        page = doc.newChild(None, "page", None)

        page.newChild(None, "title", "Index of %s" % absolute)

        location = page.newChild(None, "location", None)
        anchor = location.newChild(None, "a", "Home")
        anchor.setProp("href", "/")
        if uri:
            total_uri = ""
            for part in uri.split("/"):
                total_uri = total_uri + part + "/"
                anchor = location.newChild(None, "a", part)
                anchor.setProp("href", "/" + total_uri)

        page.newChild(None, "style", "%s/index.css" % stylepath)

        body = page.newChild(None, "content", None)

        header = os.path.join(path, "HEADER.html")
        if os.access(header, os.F_OK):
            html = xml.parseFile(header).children
            while html:
                if html.name == "html":
                    node = html.children
                    while node:
                        body.addChild(node)
                        node = node.next
                    break
                html = html.next

        listing = body.newChild(None, "index", None)
        for dirent in contents:
            entry = listing.newChild(None, "entry", None)
            for datum in dirent.keys():
                entry.newChild(None, datum, dirent[datum])

        # Add it to the request
        r.type = "text/xml"
        r.xml = doc
