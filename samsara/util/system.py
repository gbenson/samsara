import os

def system(path, *args):
    """Like os.system() but does not invoke a shell
    """
    args = (path,) + args
    pid = os.fork()
    if pid == 0:
        os.execv(path, args)

    status = os.waitpid(pid, 0)[1]
    if not os.WIFEXITED(status):
        raise RuntimeError
    return os.WEXITSTATUS(status)
