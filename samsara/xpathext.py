import re
import time
import calendar as cal
import libxml2
import libxslt
import string
from samsara.util import date

# removes leading and trailing space, leading digits, and bracketed stuff
pl_cleanup_re = re.compile(r"^\s*[\d.]*\s*(.*?)\s*([([{<].*)?\s*$")

# replaces accented ISO-8859-1 characters with their non-accented equivalents
pl_deaccent_tab = string.maketrans(
    "ÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØÙÚÛÜÝàáâãäåçèéêëìíîïñòóôõöøùúûüýÿ",
    "AAAAAACEEEEIIIINOOOOOOUUUUYaaaaaaceeeeiiiinoooooouuuuyy")

def permalink(ctx, nodeset):
    """Translate some arbitrary text into something suitable for a fragment
    """
    [node] = nodeset
    text = libxml2.xmlNode(_obj=node).getContent()
    text = text.decode("UTF-8").encode("ISO-8859-1")

    clean = pl_cleanup_re.sub(r"\1", text)
    if clean:
        text = clean.strip()

    words = map(lambda w: w.lower(),
                filter(lambda c: c.isalnum() or c.isspace(),
                       text.translate(pl_deaccent_tab)).split())
    words = [words[0]] + map(lambda w: w.capitalize(), words[1:])

    return "".join(words)

def photoname(ctx, nodeset):
    """Translate some arbitrary text into something suitable for a photo name
    """
    [node] = nodeset
    text = libxml2.xmlNode(_obj=node).getContent()
    text = text.decode("UTF-8").encode("ISO-8859-1")

    text = text.split(",", 1)[0].strip()

    words = map(lambda w: w.lower(),
                filter(lambda c: c.isalnum() or c.isspace() or c == "-",
                       text.translate(pl_deaccent_tab)).split())

    return "-".join(words)

def __strptime(stamp):
    """Make a 9-tuple from the timestamp on a diary entry
    """
    # XXX strptime() doesn't understand %Z :(
    zone = stamp[-3:]
    stamp = time.strptime(stamp, "%Y-%m-%d %H:%M:%S " + zone)
    stamp = stamp[:-1] + ({time.tzname[0]: 0, time.tzname[1]: 1}[zone],)
    return stamp

def __format_date(ctx, nodeset, format):
    """Prettify the timestamp on a diary entry
    """
    [node] = nodeset
    stamp = __strptime(libxml2.xmlNode(_obj=node).getContent())
    return date.strftime(format, stamp)

def prettydate(ctx, nodeset, frumpy=0):
    """Prettify the timestamp on a diary entry
    """
    return __format_date(ctx, nodeset, "%A %o %B %Y")

def frumpydate(ctx, nodeset):
    """Prettify the timestamp on a diary entry
    """
    return __format_date(ctx, nodeset, "%o %B %Y")

daynames = ("Sunday", "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday")
monthnames = ("January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December")

def calendar(ctx, stamps, prev, next, today):
    """Create the body of a Manila-like calendar from a set of diary entries
    """
    stamps, prev, next, today = map(lambda l: map(
        lambda n: __strptime(libxml2.xmlNode(_obj=n).getContent()), l),
        (stamps, prev, next, today))

    # Extract the dates from the supplied nodeset
    year, month = stamps[0][:2]
    days = map(lambda s: s[2], stamps)
    today = today[0][2]

    # Find the insertion node of the output document
    tctxt = libxslt.xpathParserContext(_obj=ctx).context().transformContext()
    inode = tctxt.insertNode()

    # Insert a calendar
    table = inode.newChild(None, "table", None)
    table.setProp("id", "calendar")
    table.setProp("summary", "Monthly calendar with links to each day's posts")
    table.newChild(None, "caption", time.strftime("%B %Y", stamps[0]))

    row = table.newChild(None, "tr", None)
    for day in daynames:
        cell = row.newChild(None, "th", day[:2])
        cell.setProp("abbr", day)

    cal.setfirstweekday(cal.SUNDAY)
    for week in cal.monthcalendar(year, month):
        row = table.newChild(None, "tr", None)
        for day in week:
            if not day:
                row.newChild(None, "td", None)
            elif day == today:
                cell = row.newTextChild(None, "td", str(day))
                cell.setProp("class", "today")
            elif day not in days:
                row.newTextChild(None, "td", str(day))
            else:
                cell = row.newChild(None, "td", None)
                link = cell.newTextChild(None, "a", str(day))
                link.setProp("href", "/diary/%04d/%02d/%02d/" % (year,
                                                                 month,
                                                                 day))

    row = table.newChild(None, "tr", None)
    cell = row.newChild(None, "td", None)
    cell.setProp("colspan", "7")
    if prev:
        link = cell.newChild(None, "a", time.strftime("&#171;%B", prev[0]))
        link.setProp("href", time.strftime("/diary/%Y/%m/%d/", prev[0]))
    else:
        cell.addContent(monthnames[(month + 10) % 12])

    cell.addContent(" ")
    if next:
        link = cell.newChild(None, "a", time.strftime("%B&#187;", next[0]))
        link.setProp("href", time.strftime("/diary/%Y/%m/%d/", next[0]))
    else:
        cell.addContent(monthnames[month % 12])

    return ""

class EncodeError(Exception):
    """There is an error in the supplied XML
    """
    pass

def entityencode(ctx, nodeset):
    """Return an entity-encoded string suitable for an RSS feed
    """
    def encodeText(txt):
        return txt.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        
    def encodeNodeset(node):
        output = ""
        while node:
            if node.type == "element":
                output += "<%s" % node.name
                attr = node.properties
                while attr:
                    value = node.prop(attr.name)
                    # HACK: bah, RSS parsers don't seem to honour URL bases
                    if (node.name == "a" and attr.name == "href" or
                        node.name == "img" and attr.name == "src") \
                           and value[0] == "/":
                        value = "http://inauspicious.org" + value
                    output += ' %s="%s"' % (attr.name, encodeText(value))
                    attr = attr.next
                if node.children:
                    output += ">"
                    output += encodeNodeset(node.children)
                    output += "</%s>" % node.name
                else:
                    output += "/>"
            elif node.type == "text":
                output += encodeText(node.getContent())
            else:
                raise EncodeError, "unexpected '%s' node" % node.type
            node = node.next
        return output

    # HACK: don't know if this is valid but it does the trick
    return encodeNodeset(libxml2.xmlNode(_obj=nodeset[0]))
    # This is broken; should be encodeNode() instead:
    #return reduce(lambda x, y: x + y,
    #              map(lambda n: encodeNodeset(libxml2.xmlNode(_obj=n)),
    #                  nodeset))
