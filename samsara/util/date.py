import time

def ordinal(date):
    """Return the English ordinal suffix of a date
    """
    if date / 10 == 1:
        return "th"
    else:
        return {1: "st", 2: "nd", 3: "rd"}.get(date % 10, "th")

def strftime(format, stamp):
    """Like time.strftime() but with an extra option %o
    """
    return time.strftime(format, stamp).replace("%o", "%d%s" % (
        stamp[2], ordinal(stamp[2])))
