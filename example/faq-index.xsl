<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ssr="http://inauspicious.org/samsara"
  extension-element-prefixes="ssr">

  <xsl:param name="showAll"/>

  <xsl:output method="xml" doctype-system="page.dtd"/>

  <!--

   Note that questions are expected to be selected in the following ways:

    1. From the "Find out more" boxes, on the main page and on other
       answers.

    2. From the "Most popular questions" page, linked from the navbar
       and from the bottom of the main page's "Find out more" box.

    3. From the "All questions" page, linked only from the "Most
       popular questions" page.

   So while _some_ users may hit the link in the navbar, and _some_
   users may hit the "Show more questions..." link in the main page's
   "Find out more" box, the vast majority of users will enter the
   questions by selecting one directly from the main page's "Find out
   more" box.  This means that the exact details of the two indexes
   created by this file are of a lower priority than other parts of
   the site.

   -->

  <xsl:template match="faq">
    <xsl:processing-instruction name="xml-stylesheet">
      <xsl:text>href="page.xsl" type="text/xsl"</xsl:text>
    </xsl:processing-instruction>
    <page>
      <head>
        <title>
          <!-- xsl:choose>
            <xsl:when test="$showAll = 'yes'">
              All questions
            </xsl:when>
            <xsl:otherwise -->
              Questions
            <!-- /xsl:otherwise>
          </xsl:choose -->
        </title>
        <copyright><xsl:value-of select="copyright"/></copyright>
        <robots>noindex</robots>
      </head>
      <body>
        <ul>
          <xsl:choose>
            <xsl:when test="$showAll = 'yes'">
              <xsl:apply-templates select="entries/entry"/>
            </xsl:when>
            <xsl:otherwise>
              <xsl:apply-templates select="entries/entry[@top = 'yes']"/>
            </xsl:otherwise>
          </xsl:choose>
        </ul>
        <!-- xsl:if test="$showAll != 'yes'">
          <p>
            <a href="all-questions.html">Show all questions...</a>
          </p>
        </xsl:if -->
      </body>
    </page>      
  </xsl:template>

  <xsl:template match="entry">
    <li>
      <a href="{ssr:bumpyToHyphenated(@id)}.html">
        <xsl:value-of select="normalize-space(question)"/>
      </a>
    </li>
  </xsl:template>

</xsl:stylesheet>
