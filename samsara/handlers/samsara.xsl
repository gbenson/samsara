<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml"
    doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"
    doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"/>

  <xsl:template match="page">
    <html lang="en" xml:lang="en">
      <head>
        <title>Samsara</title>
        <style type="text/css">
          body {
            margin: 0;
          }
          h1 {
            margin: 0;
            padding: 0.5em;
            background-color: navy;
            color: white;
          }
          h1, h2 {
            font-family: tahoma, arial, helvetica, sans-serif;
          }
          h2 {
            font-size: 120%;
          }
          #pageWrap {
            margin: 1em;
          }
        </style>
      </head>
      <body>
        <h1>Samsara</h1>
        <div id="pageWrap">
          <xsl:apply-templates/>
        </div>          
      </body>
    </html>
  </xsl:template>

  <xsl:template match="message">
    <h2><xsl:apply-templates/></h2>
  </xsl:template>

  <xsl:template match="form">
    <form action="{@action}">
      <xsl:apply-templates/>        
    </form>
  </xsl:template>

  <xsl:template match="button">
    <input type="submit" value="{.}"/>
  </xsl:template>

</xsl:stylesheet>
