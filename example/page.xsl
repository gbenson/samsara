<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ssr="http://inauspicious.org/samsara"
  extension-element-prefixes="ssr">

  <xsl:import href="markup.xsl"/>

  <xsl:param name="uri"/>

  <xsl:output method="xml"
    doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"
    doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"/>

  <xsl:template match="page">
    <html lang="en" xml:lang="en">
      <xsl:apply-templates/>
    </html>
  </xsl:template>

  <xsl:template match="head">
    <head>
      <xsl:choose>
        <xsl:when test="$uri = '/'">
          <title>Relax Shiatsu</title>
        </xsl:when>
        <xsl:otherwise>
          <title><xsl:value-of select="title"/></title>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:apply-templates select="copyright|keywords|description|robots"/>
      <link rel="stylesheet" type="text/css" href="page.css"/>
    </head>
  </xsl:template>

  <xsl:template match="copyright">
    <meta name="copyright" content="© Copyright {.}"/>
  </xsl:template>

  <xsl:template match="keywords">
    <xsl:variable name="keywords">
      <xsl:apply-templates select="keyword"/>
    </xsl:variable>
    <meta name="keywords" content="{$keywords}"/>
  </xsl:template>

  <xsl:template match="keyword">
    <xsl:if test="position() > 1">
      <xsl:value-of select="','"/>
    </xsl:if>
    <xsl:value-of select="."/>
  </xsl:template>

  <xsl:template match="description|robots">
    <meta name="{name()}" content="{normalize-space(.)}"/>
  </xsl:template>

  <xsl:template match="body">
    <body>
      <div id="pageWrap">
        <div id="pageHead">
          <xsl:if test="$uri != '/'">
            <a id="logoLink" href="/"></a>
          </xsl:if>
          <!-- <div id="contacts">
            01225 836103<br/>
            07779 669528<br/>
            <a href="mailto:gary@relaxshiatsu.co.uk"
              >gary@relaxshiatsu.co.uk</a>
          </div> -->
        </div>
        <div id="pageBody">
          <div id="contentHead"/>
          <div id="content">
            <xsl:apply-templates select="document('navbar.xml')/navbar"/>
            <h1><xsl:value-of select="../head/title"/></h1>
            <xsl:apply-templates/>
            <xsl:call-template name="standardFooter"/>
          </div>
          <div id="contentFoot"/>
        </div>
      </div>
    </body>
  </xsl:template>

  <xsl:template match="navbar">
    <div id="navBar">
      <xsl:apply-templates select="a"/>
    </div>
  </xsl:template>

  <xsl:template match="navbar/a">
    <xsl:if test="position() > 1">
      <span class="navSep"> | </span>
    </xsl:if>
    <xsl:choose>
      <xsl:when test="@href = $uri or concat('/', @href) = $uri">
        <xsl:value-of select="."/>
      </xsl:when>
      <xsl:otherwise>
        <a href="{@href}"><xsl:value-of select="."/></a>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="findoutmore">
    <div id="findOutMore">
      <div id="findOutMoreHead">
        <h2>Find out more:</h2>
      </div>
      <div id="findOutMoreBody">
        <ul>
          <xsl:apply-templates>
            <xsl:with-param name="faq" select="document('faq.xml')/faq"/>
          </xsl:apply-templates>
        </ul>
      </div>
      <a id="allQuestions" href="questions.html">see all questions</a>
    </div>
  </xsl:template>

  <xsl:template match="faq">
    <xsl:param name="faq"/>
    <xsl:variable name="link" select="ssr:bumpyToHyphenated(@question)"/>
    <xsl:variable name="question" select="@question"/>
    <xsl:variable name="text">
      <xsl:choose>
        <xsl:when test="@text">
          <xsl:value-of select="@text"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="normalize-space(
            $faq/entries/entry[@id = $question]/question)"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <li>
      <a href="{$link}.html">
        <xsl:value-of select="$text"/>
      </a>
    </li>
  </xsl:template>

  <xsl:template match="abbr">
    <xsl:value-of select="translate(
      @title, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"/>
    <span class="abbreviation">
      <xsl:value-of select="concat(' (', ., ')')"/>      
    </span>
  </xsl:template>
  
  <xsl:template match="ssi">
    <xsl:comment>
      <xsl:value-of select="concat(normalize-space(.), ' ')"/>
    </xsl:comment>
  </xsl:template>

  <xsl:template name="standardFooter">
    <p id="standardFooter">
      Relax Shiatsu is the Bath shiatsu practice of Gary Benson.  <!-- For
      more information or to book a treatment call 01225&#160;836103
      or 07779&#160;669528 or email <a
      href="mailto:gary@relaxshiatsu.co.uk">gary@relaxshiatsu.co.uk</a>.
      Evening appointments are available. -->
    </p>
  </xsl:template>

</xsl:stylesheet>
