import unittestsource
from samsara.handlers import file

# Contents of various files
index_xml = """\
DOCUMENT
version=1.0
URL=%s/index.xml
standalone=true
  ELEMENT index-xml
"""

other_xml = """\
DOCUMENT
version=1.0
URL=%s/other.xml
standalone=true
  ELEMENT other-xml
"""

index_html = "<index-html/>\n"

index_css = "/* CSS */\n"

file_noext = "FILE\n"

class FileTestCase(unittestsource.TestCase):
    """Base class for all file testcases
    """
    handler = file.FileHandler

class FileTestXMLIndex(FileTestCase):
    dir = "xmlindex"

    def testSlashServe(self):
        self.checkDeclined("/")

    def testIndexXmlServe(self):
        self.checkSuccess("/index.xml", "text/xml", index_xml % self.dir)

    def testOtherXmlServe(self):
        self.checkSuccess("/other.xml", "text/xml", other_xml % self.dir)

    def testIndexHtmlServe(self):
        self.checkSuccess("/index.html", "text/html", index_html)

    def testIndexCssServe(self):
        self.checkSuccess("/index.css", "text/css", index_css)

    def testNotThereServe(self):
        self.checkDeclined("/not.there")

class FileTestHTMLIndex(FileTestCase):
    dir = "htmlindex"

    def testSlashServe(self):
        self.checkDeclined("/")

    def testIndexXmlServe(self):
        self.checkDeclined("/index.xml")

    def testOtherXmlServe(self):
        self.checkSuccess("/other.xml", "text/xml", other_xml % self.dir)

    def testIndexHtmlServe(self):
        self.checkSuccess("/index.html", "text/html", index_html)

    def testIndexCssServe(self):
        self.checkSuccess("/index.css", "text/css", index_css)

    def testNotThereServe(self):
        self.checkDeclined("/not.there")

class FileTestCSSIndex(FileTestCase):
    dir = "cssindex"

    def testSlashServe(self):
        self.checkDeclined("/")

    def testIndexXmlServe(self):
        self.checkDeclined("/index.xml")

    def testOtherXmlServe(self):
        self.checkSuccess("/other.xml", "text/xml", other_xml % self.dir)

    def testIndexHtmlServe(self):
        self.checkDeclined("/index.html")

    def testIndexCssServe(self):
        self.checkSuccess("/index.css", "text/css", index_css)

    def testNotThereServe(self):
        self.checkDeclined("/not.there")

class FileTestNoIndex(FileTestCase):
    dir = "noindex"

    def testSlashServe(self):
        self.checkDeclined("/")

    def testIndexXmlServe(self):
        self.checkDeclined("/index.xml")

    def testOtherXmlServe(self):
        self.checkSuccess("/other.xml", "text/xml", other_xml % self.dir)

    def testIndexHtmlServe(self):
        self.checkDeclined("/index.html")

    def testIndexCssServe(self):
        self.checkDeclined("/index.css")

    def testNotThereServe(self):
        self.checkDeclined("/not.there")

class FileTestDirHandling(FileTestCase):
    dir = "dir"

    def testSlashServe(self):
        self.checkDeclined("/")

    def testDirServe(self):
        self.checkDeclined("/dir/")

    def testFileServe(self):
        self.checkSuccess("/file", "text/plain", file_noext)

    def testDirFailServe(self):
        self.checkDeclined("/dir")

    def testFileFailServe(self):
        self.checkDeclined("/file/")

    def testNestedServe(self):
        self.checkDeclined("/nested/")

    def testNestedDirServe(self):
        self.checkDeclined("/nested/dir/")

    def testNestedFileServe(self):
        self.checkSuccess("/nested/dir/file", "text/plain", file_noext)
