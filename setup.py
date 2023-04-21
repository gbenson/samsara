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
    """Strip path-modification preambles from scripts."""
    def run(self):
        install_scripts.run(self)
        if self.dry_run:
            return
        for filename in self.get_outputs():
            with open(filename) as fp:
                lines = fp.readlines()
            lines[1:lines.index("### end of preamble\n") + 1] = []
            with open(filename, "w") as fp:
                fp.writelines(lines)

setup(
    name="samsara",
    version="0.1",
    packages=find_packages(),
    scripts=list(sorted(glob.glob(os.path.join("bin", "*")))),
    cmdclass={
        'install_scripts': InstallScriptsCommand,
    },
)
