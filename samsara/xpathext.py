import re
import time
import calendar as cal
import libxml2
import libxslt

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

def prettydate(ctx, nodeset):
    """Prettify the timestamp on a diary entry
    """
    [node] = nodeset
    stamp = libxml2.xmlNode(_obj=node).getContent()

    # XXX strptime() doesn't understand %Z :(
    zone = stamp[-3:]
    stamp = time.strptime(stamp, "%Y-%m-%d %H:%M:%S " + zone)
    stamp = stamp[:-1] + ({time.tzname[0]: 0, time.tzname[1]: 1}[zone],)

    date = stamp[2]
    day = time.strftime("%A", stamp)

    ten, unit = date/10, date%10
    if ten != 1 and unit>0 and unit<4:
        ordinal = ["st", "nd", "rd"][unit - 1]
    else:
        ordinal = "th"

    return "%s %d%s" % (day, date, ordinal)

def calendar(ctx, nodeset):
    """Create the body of a Manila-like calendar from a set of diary entries
    """
    stamps = map(lambda n: libxml2.xmlNode(_obj=n).prop("date"), nodeset)

    # Extract the dates from the supplied nodeset
    yrmon = stamps[0][:7]
    if map(lambda s: s[:7], stamps) != [yrmon] * len(stamps):
        raise RuntimeError, "more than one month's worth of entries"
    year, month = map(int, (yrmon[:4], yrmon[5:7]))
    days = map(lambda s: int(s[8:10]), stamps)

    # Find the insertion node of the output document
    tctxt = libxslt.xpathParserContext(_obj=ctx).context().transformContext()
    table = tctxt.insertNode()

    # Insert a calendar
    cal.setfirstweekday(cal.SUNDAY)
    for week in cal.monthcalendar(year, month):
        row = table.newChild(None, "tr", None)
        for day in week:
            if not day:
                row.newChild(None, "td", None)
            elif day not in days:
                row.newTextChild(None, "td", str(day))
            else:
                cell = row.newChild(None, "td", None)
                link = cell.newTextChild(None, "a", str(day))
                link.setProp("href", "#%d" % day)

    return ""
