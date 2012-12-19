from samsara import server

# I got rid of all the pointless xmlns things.
# Make sure none sneak back in!

class XMLNSChecker(server.HandlerClass):
    priority = -100

    allowed = (
        'xmlns="http://www.w3.org/1999/xhtml',
        'xmlns:atom="http://www.w3.org/2005/Atom',
        'xmlns:dc="http://purl.org/dc/elements/1.1/')

    def handle(self, r):
        if r.payload is None:
            # Don't try and process non-existing URLs
            return
        if isinstance(r.payload, server.File):
            # Anything we're spooling from the disk is assumed to be ok
            return
        if r.uri == "samsara/":
            # Contains the string "xmlns" because it's this file's name
            return
        text = r.payload

        start = 0
        found = []
        while True:
            start = text.find("xmlns", start)
            if start < 0:
                break
            limit = text.find("=", start)
            assert limit > start
            quote = text[limit + 1]
            assert quote in "\"'"
            limit = text.find(quote, limit + 2)
            thing = text[start:limit]
            assert thing in self.allowed
            assert thing not in found
            found.append(thing)
            start = limit + 1
