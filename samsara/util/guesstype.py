import mimetypes

# mimetypes doesn't know where Red Hat put the MIME types file
mimetypes.init(["/etc/mime.types"])

encodings_map = {None:       None,
                 "gzip":     "application/x-gzip",
                 "compress": "application/x-compress"}

def guessType(path):
    """Guess the MIME type of a file based on its filename or URL.

    This function attempts to return the 'outermost' type, and would return
    'application/x-gzip' for the file 'foo.ps.gz'.
    """
    mimetype, encoding = mimetypes.guess_type(path)
    return encodings_map[encoding] or mimetype or "text/plain"

def guessBaseType(path):
    """Guess the MIME type of a file based on its filename or URL.

    This function attempts to return the 'innermost' type, and would return
    'application/postscript' for the file 'foo.ps.gz'.
    """
    mimetype, encoding = mimetypes.guess_type(path)
    return mimetype or "text/plain"
