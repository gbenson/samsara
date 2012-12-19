import xml.sax.saxutils as saxutils
from samsara import server

class RSSCDATAHandler(server.HandlerClass):
    priority = -85

    PREFIX = "<description>"
    SUFFIX = "</description>"

    def handle(self, r):
        if isinstance(r.payload, server.File):
            return
        if not r.uri.endswith(".xml"):
            return
        if not r.payload.rstrip().endswith("</rss>"):
            return

        src, dst, pos = r.payload, [], 0
        while True:
            start = src.find(self.PREFIX, pos)
            if start < 0:
                break
            start += len(self.PREFIX)
            limit = src.find(self.SUFFIX, start)
            assert limit > start
            dst.append(src[pos:start])
            tmp1 = src[start:limit]
            tmp2 = saxutils.unescape(tmp1)
            clean = tmp1 == tmp2
            if not clean:
                dst.append("<![CDATA[")
            dst.append(tmp2)
            if not clean:
                dst.append("]]>")
            pos = limit + len(self.SUFFIX)
            dst.append(src[limit:pos])
        dst.append(src[pos:])
        r.payload = "".join(dst)
