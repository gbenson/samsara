import sys
import os
import imp
import glob

class Loader:
    """Manage the loading and unloading of a directory full of modules
    """

    def __init__(self, paths, prefix):
        """Constructor: may be extended, do not override.
        """
        self.paths = paths
        self.prefix = prefix + "."
        self.names = []
        self.auto_update = True
        self.is_loaded = False

    def updateCache(self):
        """Rescan the directory of modules and synchronize with it
        """
        if not self.auto_update:
            return
        self.is_loaded = True

        # Build a list of module names which represents our current set
        names = {}
        for path in self.paths:
            for name in filter(lambda n: n != "__init__",
                               map(lambda p: os.path.split(p)[1][:-3],
                                   glob.glob(os.path.join(path, "*.py")))):
                names[name] = 1
        names = names.keys()

        # Unload modules whose files have been deleted
        for name in self.names:
            if name not in names:
                if hasattr(self, "moduleUnloaded"):
                    self.moduleUnloaded(name)
                del sys.modules[self.prefix + name]
        self.names = names

        # Load new modules and reload changed ones as necessary
        for name in names:
            fullname = self.prefix + name

            if sys.modules.has_key(fullname):
                # Already loaded, reload if necessary
                old_mtime = sys.modules[fullname].__mtime__
                mtime = module_mtime(sys.modules[fullname])
            else:
                # Not yet loaded
                mtime, old_mtime = 0, -1

            if mtime != old_mtime:
                # Create dummy modules for parents as necessary
                items = fullname.split(".")
                for i in xrange(1, len(items)):
                    parent = ".".join(items[:i])
                    if sys.modules.has_key(parent):
                        continue
                    sys.modules[parent] = imp.new_module(parent)

                # Now (re)load the module
                f, p, d = imp.find_module(name, self.paths)
                try:
                    module = imp.load_module(fullname, f, p, d)
                finally:
                    if f:
                        f.close()

                if mtime == 0:
                    mtime = module_mtime(module)
                module.__mtime__ = mtime

                if hasattr(self, "moduleLoaded"):
                    self.moduleLoaded(name, module)

def module_mtime(module):
    """Work out the mtime of a loaded module
    """
    file = module.__file__
    if os.path.exists(file[:-1]):
        file = file[:-1]
    return os.path.getmtime(file)

