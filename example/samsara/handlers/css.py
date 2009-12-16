import re
import samsara.server

class CSSCommenttripper(samsara.server.HandlerClass):
    priority = -100
    strip = re.compile(r"/\*.*?\*/", re.S)

    def handle(self, r):
        if r.type != "text/css":
            return
        r.payload = "\n".join([
            l2 for l2 in [
                l1.rstrip()
                for l1 in self.strip.sub("", r.getPayload()).split("\n")]
            if l2]) + "\n"
