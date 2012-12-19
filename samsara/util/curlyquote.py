import re

LEFT, RIGHT = 0, 1
QUOTES = {1: (u"\u2018", u"\u2019"), 2: (u"\u201c", u"\u201d")}
ENDINGS = ".,?!])-"

def process_quote(pre, post, quote):
    if pre and not post:
        if pre[-1].isspace():
            side = LEFT
        else:
            side = RIGHT
    elif post and not pre:
        if post[0].isspace() or post[0] in ENDINGS:
            side = RIGHT
        else:
            side = LEFT
    elif pre[-1].isspace() and not post[0].isspace():
        side = LEFT
    elif not pre[-1].isspace() and (post[0].isspace() or post[0] in ENDINGS):
        side = RIGHT
    return pre + QUOTES[quote][side], post

def process_apostrophe(pre, post):
    i = len(pre) - 1
    while i >= 0:
        if pre[i].isspace() or pre[i] == "(":
            i += 1
            break
        i -= 1
    if i < 0:
        i = 0
    j = 0
    while j < len(post):
        if post[j].isspace() or post[j] in ENDINGS:
            break
        j += 1
    word = pre[i:] + "'" + post[:j]
    if word == "'s" or not word.startswith("'"):
        for ending in ("'s", "s'", "n't", "'ll", "'m", "'ve", "'d", "'re"):
            if word.endswith(ending):
                return pre + u"\u2019", post
    return process_quote(pre, post, 1)

def process_double_quote(pre, post):
    return process_quote(pre, post, 2)

def process_ampersand(pre, post):
    i = post.find(";")
    assert i >= 0
    assert post[:i] in ("amp", "gt", "lt")
    return pre + "&" + post[:i + 1], post[i + 1:]

def process_endash(pre, post):
    assert post != '-'
    return pre.rstrip() + u"\u2013", post.lstrip()

def process_emdash(pre, post):
    assert post != '-'
    return pre.rstrip() + u"\u2014", post.lstrip()

def process_ellipsis(pre, post):
    return pre + u"\u2026", post

def process_copyright(pre, post):
    return pre + u"\u00a9", post

processable = re.compile(
    r"^(.*?)([&'" + '"' + r"]|---?|\.\.\.|\(C\))(.*)$", re.S)
processors  = {
    "'":   process_apostrophe,
    '"':   process_double_quote,
    "&":   process_ampersand,
    "--":  process_endash,
    "---": process_emdash,
    "...": process_ellipsis,
    "(C)": process_copyright}

def curlyquote_cdata(src):
    dst = []
    while src:
        match = processable.search(src)
        if not match:
            dst.append(src)
            break
        pre, what, post = match.groups()
        done, todo = processors[what](pre, post)
        dst.append(done)
        src = todo
    return "".join(dst)

def curlyquote_tag(src):
    assert src[0] == "<"
    dst, l, i = [], len(src), 1
    # Back over the end
    assert src[l - 1] == ">"
    l -= 1
    if src[l - 1] == "/":
        l -= 1
    while src[l - 1].isspace():
        l -= 1
    # Do the start
    while i < l and not src[i].isspace():
        i += 1
    dst.append(src[:i])
    # Do the attributes
    while i < l:
        assert src[i].isspace()
        j = i
        while src[j].isspace():
            j += 1
        k = j
        while src[k] != "=":
            k += 1
        name = src[j:k]
        k += 1
        assert src[k] == '"'
        k += 1
        m = src.find('"', k)
        assert m >= k
        value = src[k:m]
        n = m + 1
        if name in ("alt", "title") or \
           name == "content" and src[:j].endswith('meta name="copyright" '):
            value = curlyquote_cdata(value)
        dst.append(src[i:k] + value + src[m:n])
        i = n
    dst.append(src[l:])
    return "".join(dst)

def curlyquote(src):
    dst, l, i = [], len(src), 0
    noprocess = []
    while i < l:
        if src[i] == '<':
            if src[i + 1:i + 22] == "description><![CDATA[":
                # Description element of an RSS feed
                j = src.find("]]></description>", i)
                assert j > i
                j += 18
                chunk = src[i:j]
                chunk = (chunk[:22] +
                         curlyquote(chunk[22:-17]) +
                         chunk[-17:])
            else:
                # Element (or whatever)
                for tag in ("pre", "code", "script"):
                    if (src[i + 1:].startswith(tag) and
                        (src[i + 1 + len(tag)] == '>' or
                         src[i + 1 + len(tag)].isspace())):
                        noprocess.append("</%s>" % tag)
                        break
                end = ">"
                j = src.find(end, i)
                assert j > i
                j += 1
                chunk = src[i:j]
                if noprocess and noprocess[-1] == chunk:
                    noprocess.pop()
                if chunk[1] not in "/?!":
                    chunk = curlyquote_tag(chunk)
        else:
            # Stuff between tags
            j = src.find('<', i)
            if j < 0:
                j = l
            chunk = src[i:j]
            if not noprocess:
                chunk = curlyquote_cdata(chunk)
                for c in "\"'":
                    if c in chunk:
                        raise ValueError, repr(chunk)
        dst.append(chunk)
        i = j
    return "".join(dst)

if __name__ == "__main__":
    for path in open("cq.test", "r").readlines():
        path = "staging/inauspicious.org/" + path.rstrip()
        if path.endswith("/"):
            path += "index.html"
        elif path.endswith(".xml"):
            path = path[:-3] + "html"
        print path
        plain = open(path, "r").read().decode("utf-8")
        curly = curlyquote(plain)
        if plain != curly:
            open("plain", "w").write(plain.encode("utf-8"))
            open("curly", "w").write(curly.encode("utf-8"))
