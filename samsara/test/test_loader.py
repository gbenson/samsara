import unittest
from samsara.util import loader

import sys
import os
import tempfile
from samsara.util import intercept

# Loaders with different combinations of callbacks
class TestLoaderNeither(loader.Loader):
    pass

class TestLoaderLoadOnly(loader.Loader):
    def moduleLoaded(self, name, module):
        print "moduleLoaded(%s)" % name

class TestLoaderUnloadOnly(loader.Loader):
    def moduleUnloaded(self, name):
        print "moduleUnloaded(%s)" % name

class TestLoaderBoth(loader.Loader):
    def moduleLoaded(self, name, module):
        print "moduleLoaded(%s)" % name
    def moduleUnloaded(self, name):
        print "moduleUnloaded(%s)" % name

# Tests and their expected results
#
# The test sequence is:
# 1. create two modules, a and b
# 2. do nothing
# 3. touch b
# 4. delete a
# 5. recreate a
tests = ((TestLoaderNeither,
          ("import(a)\nimport(b)\n",
           "",
           "import(b)\n",
           "",
           "import(a)\n")),
         (TestLoaderLoadOnly,
          ("import(a)\nmoduleLoaded(a)\nimport(b)\nmoduleLoaded(b)\n",
           "",
           "import(b)\nmoduleLoaded(b)\n",
           "",
           "import(a)\nmoduleLoaded(a)\n")),
         (TestLoaderUnloadOnly,
          ("import(a)\nimport(b)\n",
           "",
           "import(b)\n",
           "moduleUnloaded(a)\n",
           "import(a)\n")),
         (TestLoaderBoth,
          ("import(a)\nmoduleLoaded(a)\nimport(b)\nmoduleLoaded(b)\n",
           "",
           "import(b)\nmoduleLoaded(b)\n",
           "moduleUnloaded(a)\n",
           "import(a)\nmoduleLoaded(a)\n")))

class LoaderTestCase(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mktemp()
        os.mkdir(self.dir)
        self.prefix = "test.modules"

    def tearDown(self):
        self.deleteModule("a")
        self.deleteModule("b")
        os.rmdir(self.dir)

    def testLoader(self):
        for test, responses in tests:
            self.loader = test([self.dir], self.prefix)

            self.createModule("a")
            self.createModule("b")
            self.doOneTest(responses[0], ["a", "b"])

            self.doOneTest(responses[1], ["a", "b"])

            sys.modules[self.prefix + ".b"].__mtime__ -= 1
            self.doOneTest(responses[2], ["a", "b"])

            self.deleteModule("a")
            self.doOneTest(responses[3], ["b"])
            
            self.createModule("a")
            self.doOneTest(responses[4], ["a", "b"])

            del sys.modules[self.prefix + ".a"]
            del sys.modules[self.prefix + ".b"]

    def createModule(self, module):
        open(os.path.join(self.dir, module + ".py"), "w").write(
            "print 'import(%s)'" % module)

    def deleteModule(self, module):
        os.remove(os.path.join(self.dir, module + ".py"))
        os.remove(os.path.join(self.dir, module + ".pyc"))

    def doOneTest(self, expect_out, expect_loaded):
        out = intercept.intercept(intercept.STDOUT, self.loader.updateCache)[1]
        self.assertEqual(out, expect_out)
        loaded = map(lambda n: n[len(self.prefix) + 1:],
                     filter(lambda n: n.startswith(self.prefix + "."),
                            sys.modules.keys()))
        loaded.sort()
        self.assertEqual(loaded, expect_loaded)
