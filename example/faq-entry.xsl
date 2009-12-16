<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ssr="http://inauspicious.org/samsara"
  xsl:exclude-result-prefixes='ssr'>

  <xsl:import href="markup.xsl"/>

  <xsl:param name="entry"/>

  <xsl:output method="xml" doctype-system="page.dtd"/>

  <xsl:template match="faq">
    <xsl:apply-templates select="entries/entry[@id = $entry]"/>
  </xsl:template>

  <xsl:template match="entry">
    <xsl:processing-instruction name="xml-stylesheet">
      <xsl:text>href="page.xsl" type="text/xsl"</xsl:text>
    </xsl:processing-instruction>
    <page>
      <head>
        <title><xsl:value-of select="question"/></title>
        <copyright><xsl:value-of select="../../copyright"/></copyright>
      </head>
      <body>
        <xsl:apply-templates select="answer"/>
        <xsl:apply-templates select="links"/>
      </body>
    </page>      
  </xsl:template>

  <xsl:template match="answer">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="links">
    <findoutmore>
      <xsl:apply-templates/>
    </findoutmore>
  </xsl:template>

  <xsl:template match="link">
    <faq question="{@question}"/>
  </xsl:template>

</xsl:stylesheet>
