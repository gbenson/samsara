from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# Python2 distutils can't cope with __future__.unicode_literals

from setuptools import find_packages, setup
from setuptools.command.install_scripts import install_scripts
from distutils import log
import glob
import os

class InstallScriptsCommand(install_scripts):
    """Rename scripts with "samsara-" prefixes."""
    def run(self):
        install_scripts.run(self)
        new_outfiles = []
        for orig_filename in self.get_outputs():
            dirname, basename = os.path.split(orig_filename)
            basename = {"unittest": "test"}.get(basename, basename)
            basename = "samsara-" + basename
            log.info("renaming %s to %s", orig_filename, basename)
            filename = os.path.join(dirname, basename)
            if not self.dry_run:
                os.link(orig_filename, filename)
                os.unlink(orig_filename)
            new_outfiles.append(filename)
        self.outfiles = new_outfiles

setup(
    name="samsara",
    version="0.1",
    packages=find_packages(),
    scripts=list(sorted(glob.glob(os.path.join("bin", "*")))),
    cmdclass={
        'install_scripts': InstallScriptsCommand,
    },
)
