import sys
import os
import tempfile

STDOUT = 1
STDERR = 2

def intercept(what, callable, *args, **kwargs):
    """Intercept stdout and/or stderr during a function call

    The what argument is a bitmask denoting which streams to be
    intercepted.  Possible values are STDOUT and STDERR.
    """
    if not (what & STDOUT or what & STDERR):
        raise ValueError, "no streams specified for redirection"

    fn = tempfile.mktemp()
    fd = os.open(fn, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0600)

    try:
        if what & STDOUT:
            sys.stdout.flush()
            saved_stdout_fd = os.dup(1)
            os.dup2(fd, 1)

        if what & STDERR:
            sys.stderr.flush()
            saved_stderr_fd = os.dup(2)
            os.dup2(fd, 2)

        try:
            result = apply(callable, args, kwargs)

        finally:
            if what & STDOUT:
                sys.stdout.flush()
                os.dup2(saved_stdout_fd, 1)
                os.close(saved_stdout_fd)

            if what & STDERR:
                sys.stderr.flush()
                os.dup2(saved_stderr_fd, 2)
                os.close(saved_stderr_fd)

    finally:
        size = os.lseek(fd, 0, 1)
        os.lseek(fd, 0, 0)
        redirected = os.read(fd, size)

        os.close(fd)
        os.unlink(fn)

    return result, redirected
