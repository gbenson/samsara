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
                         "top: %dpx" % (8 + 18 * index),
                         "right: 7px",
                         "width: 16px",
                         "height: 16px",
                         "opacity: 0.25",
                         "background-color: #888",
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
        index = payload.find("</body>")
        if index < 0:
            return
        r.payload = payload[:index] + "\n".join(self.html(r)) + payload[index:]
