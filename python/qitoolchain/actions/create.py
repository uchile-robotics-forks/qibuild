## Copyright (C) 2011 Aldebaran Robotics

""" Create a toolchain.
    This will create all necessary directories.
"""

import os
import logging
import ConfigParser

import qibuild
import qitoolchain

LOGGER = logging.getLogger("actions.qitoolchain.create")

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.cmdparse.default_parser(parser)
    parser.add_argument("toolchain_name", metavar="NAME", action="store", help="the toolchain name")

def do(args):
    """ Main method """
    toolchain_name = args.toolchain_name
    qitoolchain.create(toolchain_name)
    toolchain = qitoolchain.Toolchain(toolchain_name)

    toolchain_names = qitoolchain.get_toolchain_names()
    if toolchain_name in toolchain_names:
        raise Exception("Toolchain %s already exists in configuration" % toolchain_name)

    qitoolchain.set_tc_config(toolchain_name, "path", toolchain.path)
