from samsara import server

class URLNormalizer(server.HandlerClass):
    priority = -70

    def handle(self, r):
        if r.type != "text/xml":
            return

        fullprefix = "/" + r.uri
        prefix = fullprefix[:fullprefix.rfind("/") + 1]

        for node in r.payload.xpathEval("//@href|//@src"):
            value = node.getContent()
            if not value:
                continue
            if value == prefix and not fullprefix.endswith("/"):
                continue
            if not value.startswith(prefix):
                continue
            node.setContent(value[len(prefix):])
