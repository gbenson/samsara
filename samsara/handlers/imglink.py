from samsara import server
import re

class ImgLinkHandler(server.HandlerClass):
    priority = -85

    expr = re.compile(
        r"""^(.*?)""" +
        r"""(<a(?:\s+\w+\s*=\s*(['"]).*?\3)\s*>)\s*""" +
        r"""(<img(?:\s+\w+\s*=\s*(['"]).*?\5)\s*/>)\s*""" +
        r"""(</a>)""" +
        r"""(.*)$""", re.S)

    def handle(self, r):
        if r.payload is None:
            # Don't try and process non-existing URLs
            return
        if isinstance(r.payload, server.File):
            # Anything we're spooling from the disk is assumed to be ok
            return

        src, dst = r.payload, ""
        while src:
            match = self.expr.match(src)
            if not match:
                dst += src
                break
            a, b, c, d, src = match.group(1, 2, 4, 6, 7)
            dst += a + b + c + d
        r.payload = dst
