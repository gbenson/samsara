def nodeToString(node, encoding = None):
    """Convert an argument into a string
    """
    if hasattr(node, "getContent"):
        node = node.getContent()
    if encoding is not None:
        node = node.decode("UTF-8").encode(encoding)
    return node

def nodesetToString(nodeset, encoding = None):
    """Convert a nodeset into a strings
    """
    [node] = nodeset
    return nodeToString(node, encoding)

def nodesetToStrings(nodeset, encoding = None):
    """Convert a nodeset into a list of strings
    """
    return map(lambda n: nodeToString(n, encoding), nodeset)
