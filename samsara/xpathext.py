import re
import libxml2

# removes leading and trailing space, leading digits, and bracketed stuff
pl_cleanup_re = re.compile(r"^\s*[\d.]*\s*(.*?)\s*([([{<].*)?\s*$")

def permalink(ctx, nodeset):
    """Translate some arbitrary text into something suitable for a fragment
    """
    [node] = nodeset
    text = libxml2.xmlNode(_obj=node).getContent()

    clean = pl_cleanup_re.sub(r"\1", text)
    if clean:
        text = clean.strip()

    words = map(lambda w: w.lower(),
                filter(lambda c: c.isalnum() or c.isspace(),
                       text).split())
    words = [words[0]] + map(lambda w: w.capitalize(), words[1:])

    return "".join(words)
