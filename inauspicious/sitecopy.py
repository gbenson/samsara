import os
import re
import tempfile
from samsara.util import intercept
from samsara.util import system

class SitecopyError(Exception):
    pass

def sitecopy(database, root, site, partial = 0, auto = 0, restrict = None):
    """UNDOCUMENTED
    """

    # Read the rc file template and perform substitutions
    rc = open(os.path.join(database, "sitecopyrc.in"), "r").read()
    rc = re.compile("@DIR@").sub(root, rc)
    rc = re.compile("@NODELETE@").sub(["", "nodelete"][partial], rc)

    rcfile = os.path.join(database, "sitecopyrc")
    open(rcfile, "w").write(rc)
    try:
        # Sitecopy, hold your peace
        os.chmod(rcfile, 0600)

        # Store some stuff away
        cmd = "/usr/bin/sitecopy"
        opts = ("--rcfile", rcfile, "--storepath", database)

        # Get a listing of what has changed
        status, output = apply(intercept.intercept,
                               (intercept.STDOUT, system.system,
                                cmd) + opts + ("--flatlist", site))
        if status == 0:
            return
        if status != 1:
            raise SitecopyError, output[:-1]

        status = {"added": [], "changed": [], "deleted": [], "moved": []}
        
        in_sect = None
        for tag, item in map(lambda s: s.split("|"), output[:-1].split("\n")):
            if tag == "sitestart":
                if site != item:
                    raise ValueError, "site mismatch"
            elif tag == "siteend":
                pass
            elif tag == "sectstart":
                in_sect = item
            elif tag == "sectend":
                if in_sect != item:
                    raise ValueError, "section mismatch"
                in_sect = None
            elif tag == "item":
                status[in_sect].append(item)
            else:
                raise ValueError, "unknown tag %s" % tag
        if partial:
            status["deleted"] = []

        # Check if it is okay to continue
        if auto:
            infractions = ""
            for type in status.keys():
                if len(status[type]) > restrict[type]:
                    infractions += "%d files %s (%d allowed)\n" % (
                        len(status[type]), type, restrict[type])
            if infractions:
                raise SitecopyError, infractions[:-1]

        else:
            for type in status.keys():
                if status[type]:
                    print "\n%s:" % type.capitalize()
                    for item in status[type]:
                        print "  - %s" % item
            if raw_input("\nSure you want to carry on? [no]: ") != "yes":
                return

        # All's clear, so push the files
        if auto:
            opts += ("--quiet",)

        status = apply(system.system, (cmd,) + opts + ("--update", site))
        if status != 0:
            raise SitecopyError, "sitecopy failed with exit code %d" % status
        
    finally:
        os.unlink(rcfile)
