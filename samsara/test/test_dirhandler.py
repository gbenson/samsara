import unittestsource
from samsara.handlers import dir

# Expected directory indexes
css_index = """\
<html><head><title>Index of /</title><body><h1>Index of /</h1><ul>
<li><a href="index.css">index.css</a></li>
<li><a href="other.xml">other.xml</a></li>
</ul></body></html>
"""

no_index = """\
<html><head><title>Index of /</title><body><h1>Index of /</h1><ul>
<li><a href="other.xml">other.xml</a></li>
</ul></body></html>
"""

dir_index = """\
<html><head><title>Index of /</title><body><h1>Index of /</h1><ul>
<li><a href="dir/">dir/</a></li>
<li><a href="file">file</a></li>
<li><a href="nested/">nested/</a></li>
</ul></body></html>
"""

nested_index = """\
<html><head><title>Index of /nested</title><body><h1>Index of /nested</h1><ul>
<li><a href="../">Parent Directory</a></li>
<li><a href="dir/">dir/</a></li>
</ul></body></html>
"""

nestdir_index = """\
<html><head><title>Index of /nested/dir</title><body><h1>Index of /nested/dir</h1><ul>
<li><a href="../">Parent Directory</a></li>
<li><a href="file">file</a></li>
</ul></body></html>
"""

class DirTestCase(unittestsource.TestCase):
    """Base class for all directory testcases
    """
    handler = dir.DirHandler

class DirTestXMLIndex(DirTestCase):
    dir = "xmlindex"

    def testSlashServe(self):
        self.checkRewrite("/", "/index.xml")

    def testIndexXmlServe(self):
        self.checkDeclined("/index.xml")

    def testOtherXmlServe(self):
        self.checkDeclined("/other.xml")

    def testIndexHtmlServe(self):
        self.checkDeclined("/index.html")

    def testIndexCssServe(self):
        self.checkDeclined("/index.css")

    def testNotThereServe(self):
        self.checkDeclined("/not.there")

class DirTestHTMLIndex(DirTestCase):
    dir = "htmlindex"

    def testSlashServe(self):
        self.checkRewrite("/", "/index.html")

    def testIndexXmlServe(self):
        self.checkDeclined("/index.xml")

    def testOtherXmlServe(self):
        self.checkDeclined("/other.xml")

    def testIndexHtmlServe(self):
        self.checkDeclined("/index.html")

    def testIndexCssServe(self):
        self.checkDeclined("/index.css")

    def testNotThereServe(self):
        self.checkDeclined("/not.there")

class DirTestCSSIndex(DirTestCase):
    dir = "cssindex"

    def testSlashServe(self):
        self.checkSuccess("/", "text/html", css_index)

    def testIndexXmlServe(self):
        self.checkDeclined("/index.xml")

    def testOtherXmlServe(self):
        self.checkDeclined("/other.xml")

    def testIndexHtmlServe(self):
        self.checkDeclined("/index.html")

    def testIndexCssServe(self):
        self.checkDeclined("/index.css")

    def testNotThereServe(self):
        self.checkDeclined("/not.there")

class DirTestNoIndex(DirTestCase):
    dir = "noindex"

    def testSlashServe(self):
        self.checkSuccess("/", "text/html", no_index)

    def testIndexXmlServe(self):
        self.checkDeclined("/index.xml")

    def testOtherXmlServe(self):
        self.checkDeclined("/other.xml")

    def testIndexHtmlServe(self):
        self.checkDeclined("/index.html")

    def testIndexCssServe(self):
        self.checkDeclined("/index.css")

    def testNotThereServe(self):
        self.checkDeclined("/not.there")

class DirTestDirHandling(DirTestCase):
    dir = "dir"

    def testSlashServe(self):
        self.checkSuccess("/", "text/html", dir_index)

    def testDirServe(self):
        self.checkRewrite("/dir/", "/dir/index.xml")

    def testFileServe(self):
        self.checkDeclined("/file")

    def testDirFailServe(self):
        self.checkDeclined("/dir")

    def testFileFailServe(self):
        self.checkDeclined("/file/")

    def testNestedServe(self):
        self.checkSuccess("/nested/", "text/html", nested_index)

    def testNestedDirServe(self):
        self.checkSuccess("/nested/dir/", "text/html", nestdir_index)

    def testNestedFileServe(self):
        self.checkDeclined("/nested/dir/file")
