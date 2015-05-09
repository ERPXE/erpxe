#!/usr/bin/env python
"""ERPXE.

Usage:
  erpxe list
  erpxe render [--quiet | --verbose] [--c=<fn>]
  erpxe disable <plugin>
  erpxe enable <plugin>
  erpxe (-h | --h | --help)
  erpxe --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --c=<fn>  	Configuration file name [default: erpxe.conf].
  --quiet      print less text
  --verbose    print more text

"""
from __future__ import print_function
__author__ = "Etay Cohen-Solal & Adam Mallul"
__copyright__ = "Copyright 2015, Etay Cohen-Solal"
__license__ = "GNU"
__maintainer__ = "Etay Cohen-Solal & Adam Mallul"
__status__ = "Development"
package = "erpxe"

import os, sys

# Get version from setup.py
from pkg_resources import get_distribution, DistributionNotFound
try:
    _dist = get_distribution(package)
    # Normalize case for Windows systems
    dist_loc = os.path.normcase(_dist.location)
    here = os.path.normcase(__file__)
    if not here.startswith(os.path.join(dist_loc, package)):
        # not installed, but there is another version that *is*
        raise DistributionNotFound
except DistributionNotFound:
    __version__ = '(local)'
else:
    __version__ = _dist.version
version = __version__

def main():
    """Entry point for the 'erpxe' application script"""
    from docopt import docopt
    arguments = docopt(__doc__, version="ERPXE v" + version)
    from cli import cli
    cli(arguments)

if __name__ == "__main__":
    main()
