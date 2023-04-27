Samsara
=======

Samsara is an ancient content management system I wrote back when the
internet was fresh and Python programmers were still reeling from not
having to ``import string`` any more.  I wanted an XML application
server but no way was I installing Java, and the only real alternative
was AxKit which was Perl, also no.  Besides, my website had a 5Mb
quota on it so I didn't have room to install anything anyway, and my
experiments with PHP ended as soon as I realized it didn't do XSL.
But, I was really into Manila and Radio UserLand and that ecosystem,
and Radio ran in a super cool way: it *looked* like a server-based
webapp, but it was actually a pimped-up little HTML editor running on
your own computer and uploading static files over FTP!  Cool!  So I
mixed all of that together and wrote a thing where I could edit XML
and XSLT in Emacs, view changes instantly via a built-in webserver,
then generate static files for upload when I was done.

Anyway, that's what this is.  You probably don't want to use it, but
I've Dockerized it because I still use it on one site, and Dockerizing
means I can freeze the versions of libxml2 and libxslt and never again
have to pick through 1,851 files that suddenly changed because libxml2
started inserting a carriage return after the ``<body>`` element for
some reason.

Usually you'd mount a directory into the container for Samsara to work
on, but I put a small example site in there so you can try this thing
out. You can check out my 2007 web design too, while you're at it.

Are you ready? Run this to serve the example site on http://localhost:2420/::

  docker run --rm -it -p 2420:2420/tcp gbenson/samsara server example

Hit Ctrl-C to kill it when you're done.  You can also fetch individual
pages, to debug things::

  docker run --rm -it gbenson/samsara get example /

You can generate a static site too, but you'll have to mount a
directory into the container for Samsara to write the files into::

  mkdir out
  docker run --rm -it --mount type=bind,src=$(pwd)/out,target=/work/out gbenson/samsara spider example out

For website updates I ``cd`` into a directory containing the XML
version of my site (``web``) and the directory I'll build into
(``staging``), and I run the commands with my out-of-container working
directory mounted onto the container's default working directory
(``/work``).  Doing things that way keeps relative paths the same::

  docker run --rm -it --mount type=bind,src=$(pwd),target=/work -p 2420:2420/tcp gbenson/samsara server web
  docker run --rm -it --mount type=bind,src=$(pwd),target=/work gbenson/samsara spider web staging

I've scripts to do the heavy lifting for me, but you get the picture.
