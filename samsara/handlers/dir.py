import os
from samsara import server

def listdir(path):
    """Return a list containing the names of the entries in the directory

    Identical to os.listdir except that it ignores some files.
    """
    return filter(lambda entry: (entry != "CVS" and
                                 entry[0] != "." and
                                 entry[0] != "#" and
                                 entry[-1] != "~"), os.listdir(path))

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

        # Render the page
        title = "Index of /" + path[len(self.root)+1:]
        r.type = "text/html"
        r.data = "<html><head><title>%s</title>" % title + \
                 "<body><h1>%s</h1><ul>\n" % title

        if path != self.root:
            r.data += '<li><a href="../">Parent Directory</a></li>\n'

        items = listdir(path)
        items.sort()
        for item in items:
            if os.path.isdir(os.path.join(path, item)):
                item += "/"
            r.data += '<li><a href="%s">%s</a></li>\n' % (item, item)

        r.data += "</ul></body></html>\n"
