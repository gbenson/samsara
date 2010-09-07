from samsara import server

class SamsaraButton(server.HandlerClass):
    """Add a Samsara button to pages when running in the HTTP server
    """
    priority = -80

    def html(self, r):
        html = []
        for (text, url), index in zip(r.buttons, range(len(r.buttons))):
            html.extend(
                ('<div style="%s;">' % "; ".join(
                        ("position: absolute",
                         "top: %dpx" % (3 + 18 * index),
                         "right: 3px",
                         "width: 16px",
                         "height: 16px",
                         "border: 2px solid white",
                         "background-color: #eee",
                         "font-family: arial, helvetica, sans-serif",
                         "font-size: 14px",
                         "font-weight: bold",
                         "text-align: center")),
                 '  <a style="%s" href="%s">%s</a>' % ("; ".join(
                        ("text-decoration: none",
                         "color: white")), url, text),
                 '</div>'))
        return tuple(html)

    def handle(self, r):
        if self.server.httpserver is None:
            return
        if r.type != "text/html":
            return
        if not r.buttons:
            return

        payload = r.getPayload()
        start = payload.lower().find("<body")
        if start < 0:
            return
        start = payload.find(">", start)
        start += 1
        limit = start
        while payload[limit].isspace():
            limit += 1
        sep = payload[start:limit]
        r.payload = sep.join(
            (payload[:start],) + self.html(r) + (payload[limit:],))
