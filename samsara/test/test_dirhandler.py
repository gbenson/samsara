import unittestsource
from samsara.handlers import dir

# Expected directory indexes
css_index = """\
DOCUMENT
version=1.0
URL=%s/index.xml
standalone=true
  PI xml-stylesheet
    content=href=\"style/index.xsl\" type=\"text/xsl\"
  ELEMENT page
    ELEMENT title
      TEXT
        content=Index of /
    ELEMENT location
      ELEMENT a
        ATTRIBUTE href
          TEXT
            content=/
        TEXT
          content=Home
    ELEMENT style
      TEXT
        content=style/index.css
    ELEMENT content
      ELEMENT index
        ELEMENT entry
          ELEMENT date
            TEXT
              content=2nd May 2002
          ELEMENT icon
            TEXT
              content=generic
          ELEMENT type
            TEXT
              content=text/css
          ELEMENT name
            TEXT
              content=index.css
          ELEMENT size
            TEXT
              content=10b
        ELEMENT entry
          ELEMENT date
            TEXT
              content=1st May 2002
          ELEMENT icon
            TEXT
              content=generic
          ELEMENT type
            TEXT
              content=text/xml
          ELEMENT name
            TEXT
              content=other.xml
          ELEMENT size
            TEXT
              content=13b
"""

no_index = """\
DOCUMENT
version=1.0
URL=%s/index.xml
standalone=true
  PI xml-stylesheet
    content=href=\"style/index.xsl\" type=\"text/xsl\"
  ELEMENT page
    ELEMENT title
      TEXT
        content=Index of /
    ELEMENT location
      ELEMENT a
        ATTRIBUTE href
          TEXT
            content=/
        TEXT
          content=Home
    ELEMENT style
      TEXT
        content=style/index.css
    ELEMENT content
      ELEMENT index
        ELEMENT entry
          ELEMENT date
            TEXT
              content=1st May 2002
          ELEMENT icon
            TEXT
              content=generic
          ELEMENT type
            TEXT
              content=text/xml
          ELEMENT name
            TEXT
              content=other.xml
          ELEMENT size
            TEXT
              content=13b
"""

dir_index = """\
DOCUMENT
version=1.0
URL=%s/index.xml
standalone=true
  PI xml-stylesheet
    content=href=\"style/index.xsl\" type=\"text/xsl\"
  ELEMENT page
    ELEMENT title
      TEXT
        content=Index of /
    ELEMENT location
      ELEMENT a
        ATTRIBUTE href
          TEXT
            content=/
        TEXT
          content=Home
    ELEMENT style
      TEXT
        content=style/index.css
    ELEMENT content
      ELEMENT index
        ELEMENT entry
          ELEMENT date
            TEXT
              content=5th May 2002
          ELEMENT type
            TEXT
              content=directory
          ELEMENT name
            TEXT
              content=nested/
          ELEMENT icon
            TEXT
              content=folder
        ELEMENT entry
          ELEMENT date
            TEXT
              content=3rd May 2002
          ELEMENT type
            TEXT
              content=directory
          ELEMENT name
            TEXT
              content=dir/
          ELEMENT icon
            TEXT
              content=folder
        ELEMENT entry
          ELEMENT date
            TEXT
              content=4th May 2002
          ELEMENT icon
            TEXT
              content=text
          ELEMENT type
            TEXT
              content=text/plain
          ELEMENT name
            TEXT
              content=file
          ELEMENT size
            TEXT
              content=5b
"""

nested_index = """\
DOCUMENT
version=1.0
URL=%s/index.xml
standalone=true
  PI xml-stylesheet
    content=href=\"../style/index.xsl\" type=\"text/xsl\"
  ELEMENT page
    ELEMENT title
      TEXT
        content=Index of /nested/
    ELEMENT location
      ELEMENT a
        ATTRIBUTE href
          TEXT
            content=/
        TEXT
          content=Home
      ELEMENT a
        ATTRIBUTE href
          TEXT
            content=/nested/
        TEXT
          content=nested
    ELEMENT style
      TEXT
        content=../style/index.css
    ELEMENT content
      ELEMENT index
        ELEMENT entry
          ELEMENT date
            TEXT
              content=5th May 2002
          ELEMENT type
            TEXT
              content=directory
          ELEMENT name
            TEXT
              content=dir/
          ELEMENT icon
            TEXT
              content=folder
"""

nestdir_index = """\
DOCUMENT
version=1.0
URL=%s/index.xml
standalone=true
  PI xml-stylesheet
    content=href=\"../../style/index.xsl\" type=\"text/xsl\"
  ELEMENT page
    ELEMENT title
      TEXT
        content=Index of /nested/dir/
    ELEMENT location
      ELEMENT a
        ATTRIBUTE href
          TEXT
            content=/
        TEXT
          content=Home
      ELEMENT a
        ATTRIBUTE href
          TEXT
            content=/nested/
        TEXT
          content=nested
      ELEMENT a
        ATTRIBUTE href
          TEXT
            content=/nested/dir/
        TEXT
          content=dir
    ELEMENT style
      TEXT
        content=../../style/index.css
    ELEMENT content
      ELEMENT index
        ELEMENT entry
          ELEMENT date
            TEXT
              content=5th May 2002
          ELEMENT icon
            TEXT
              content=text
          ELEMENT type
            TEXT
              content=text/plain
          ELEMENT name
            TEXT
              content=file
          ELEMENT size
            TEXT
              content=5b
"""

class DirTestCase(unittestsource.TestCase):
    """Base class for all directory testcases
    """
    handler = dir.DirHandler
    mtimes = {"index.xml":       "29/04/2002",
              "index.html":      "30/04/2002",
              "other.xml":       "01/05/2002",
              "index.css":       "02/05/2002",
              "dir/index.xml":   "03/05/2002",
              "file":            "04/05/2002",
              "nested/dir/file": "05/05/2002"}

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
        self.checkSuccess("/", "text/xml", css_index % self.dir)

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
        self.checkSuccess("/", "text/xml", no_index % self.dir)

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
        self.checkSuccess("/", "text/xml", dir_index % self.dir)

    def testDirServe(self):
        self.checkRewrite("/dir/", "/dir/index.xml")

    def testFileServe(self):
        self.checkDeclined("/file")

    def testDirFailServe(self):
        self.checkDeclined("/dir")

    def testFileFailServe(self):
        self.checkDeclined("/file/")

    def testNestedServe(self):
        self.checkSuccess("/nested/", "text/xml", nested_index % self.dir)

    def testNestedDirServe(self):
        self.checkSuccess("/nested/dir/", "text/xml", nestdir_index % self.dir)

    def testNestedFileServe(self):
        self.checkDeclined("/nested/dir/file")
