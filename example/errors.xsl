<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:param name="code"/>

  <xsl:output method="xml" doctype-system="page.dtd"/>

  <xsl:template match="errors">
    <xsl:apply-templates select="error[@code = $code]"/>
  </xsl:template>

  <xsl:template match="error">
    <xsl:processing-instruction name="xml-stylesheet">
      <xsl:text>href="page.xsl" type="text/xsl"</xsl:text>
    </xsl:processing-instruction>
    <page>
      <head>
        <title><xsl:value-of select="concat($code, ' ', short)"/></title>
        <robots>noindex,nofollow</robots>
      </head>
      <body>
        <xsl:apply-templates select="long"/>
      </body>
    </page>
  </xsl:template>

  <xsl:template match="long">
    <p>
      <xsl:apply-templates/>
    </p>
    <findoutmore>
      <faq question="whatIsShiatsu"/>
      <faq question="howShiatsuCanHelp"/>
    </findoutmore>
  </xsl:template>

  <xsl:template match="url">
    <code>
      <ssi>#echo var="REDIRECT_URL"</ssi>
    </code>
  </xsl:template>

  <xsl:template match="br">
    <br/>
  </xsl:template>

</xsl:stylesheet>
