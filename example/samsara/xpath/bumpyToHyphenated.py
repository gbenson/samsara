import samsara.xml.xpath

def bumpyToHyphenated(ctx, text):
    text = samsara.xml.xpath.nodesetToString(text, "utf-8")
    return "".join([c.islower() and c or "-" + c.lower() for c in text])
