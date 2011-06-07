## Copyright (C) 2011 Aldebaran Robotics

import os
import shlex
import logging

import qibuild.sh

LOGGER = logging.getLogger("qibuild.toc.project")

class Project:
    """ Store information about a project:
         - name
         - source directory
         - build directory
         - build configuration
         - dependencies
         - configstore (read from the qibuild.manifest file from the
                        source directory)
    """
    def __init__(self, name, directory):
        self.name            = name
        self.directory       = directory
        self.depends         = list()
        self.rdepends        = list()
        self.configstore     = qibuild.configstore.ConfigStore()

        #build related flags
        self.cmake_flags     = list()
        self.build_directory = None
        self.sdk_directory   = None
        self._custom_sdk_dir = False

        self.load_config()

    def get_sdk_dir(self):
        """ Return the SDK dir of the project.
        To use the project build results, from an other project,
        you just have to add this directory to CMAKE_PREFIX_PATH

        """
        return os.path.join(self.build_directory, "sdk")

    def load_config(self):
        """ Update project dependency list """
        qibuild_manifest = os.path.join(self.directory, "qibuild.manifest")
        self.configstore.read(qibuild_manifest)
        deps  = self.configstore.get("project", self.name, "depends", default="").split()
        rdeps = self.configstore.get("project", self.name, "rdepends", default="").split()
        self.depends.extend(deps)
        self.rdepends.extend(rdeps)

    def update_build_config(self, toc, build_directory_name):
        """ Update cmake_flags
           - add flags from the build_config (read in toc's configstore)
           - add flags from the project config (read in toc's configstore project section)
           - add flags from the command line (stored in toc.cmake_flags when toc is built)
        """
        LOGGER.debug("[%s]: Updating build config", self.name)

        #handle custom global build directory containing all projects
        singlebdir = toc.configstore.get("build", "directory", default=None)
        if singlebdir:
            if not os.path.isabs(singlebdir):
                singlebdir = os.path.join(toc.work_tree, singlebdir)
            bname = os.path.join("build-%s" % (build_directory_name), self.name)
            self.build_directory = os.path.normpath(os.path.join(singlebdir, bname))
        else:
            bname = "build-%s" % (build_directory_name)
            self.build_directory = os.path.join(self.directory, bname)

        if toc.build_type:
            self.cmake_flags.append("CMAKE_BUILD_TYPE=%s" % (toc.build_type.upper()))

        if toc.cmake_flags:
            self.cmake_flags.extend(toc.cmake_flags)

        LOGGER.debug("[%s]: cmake flags: %s", self.name, self.cmake_flags)

        #handle single sdk dir
        sdk_dir = toc.configstore.get("build", "sdk.directory", default=None)
        if sdk_dir:
            if os.path.isabs(sdk_dir):
                self.sdk_directory = sdk_dir
            else:
                self.sdk_directory = os.path.join(toc.work_tree, sdk_dir)
            bname = "sdk-%s" % (build_directory_name)
            self.sdk_directory = os.path.normpath(os.path.join(self.sdk_directory, bname))
            self._custom_sdk_dir = True
            self.cmake_flags.append("QI_SDK_DIR=%s" % (self.sdk_directory))
        else:
            #normal sdk dir in buildtree
            self.sdk_directory   = os.path.join(self.build_directory, "sdk")


    def set_custom_build_directory(self, build_dir):
        """ could be used to override the default build_directory
        """
        self.build_directory = build_dir

        #detect single sdk directory for multiple projects
        if self._custom_sdk_dir == False:
            self.sdk_directory = os.path.join(self.build_directory, "sdk")


    def __str__(self):
        res = ""
        res += "Project: %s\n" % (self.name)
        res += "  directory       = %s\n" % self.directory
        res += "  depends         = %s\n" % self.depends
        res += "  rdepends        = %s\n" % self.rdepends
        res += "  cmake_flags     = %s\n" % self.cmake_flags
        res += "  build_directory = %s" % self.build_directory
        return res


def get_qibuild_cmake_framework_path():
    """ return the path to the qiBuild Cmake framework """
    path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "cmake"))
    return qibuild.sh.to_posix_path(path)

def bootstrap(project, dep_sdk_dirs):
    """Generate the find_deps.cmake for the given project
    """
    build_dir = project.build_directory
    qibuild.sh.mkdir(build_dir, recursive=True)

    to_write  = "#############################################\n"
    to_write += "#QIBUILD AUTOGENERATED FILE. DO NOT EDIT.\n"
    to_write += "#############################################\n"
    to_write += "\n"
    to_write += "#QIBUILD CMAKE FRAMEWORK PATH:\n"
    to_write += "list(APPEND CMAKE_MODULE_PATH \"%s\")\n" % get_qibuild_cmake_framework_path()
    to_write += "\n"
    to_write += "#DEPENDENCIES:\n"
    for dep_sdk_dir in dep_sdk_dirs:
        to_write += "list(APPEND CMAKE_PREFIX_PATH \"%s\")\n" % qibuild.sh.to_posix_path(dep_sdk_dir)
    to_write += "set(CMAKE_MODULE_PATH \"${CMAKE_MODULE_PATH}\" CACHE INTERNAL \"\" FORCE)\n"
    to_write += "set(CMAKE_PREFIX_PATH \"${CMAKE_PREFIX_PATH}\" CACHE INTERNAL \"\" FORCE)\n"

    output_path = os.path.join(build_dir, "dependencies.cmake")
    with open(output_path, "w") as output_file:
        output_file.write(to_write)
    LOGGER.debug("Wrote %s", output_path)

def name_from_directory(project_dir):
    """Get the project name from the project directory

    The directory should contain a "qibuild.manifest" file,
    looking like

        [project foo]
        ...

    If such a section can not be found, simply return
    the base name of the directory
    """
    manifest = os.path.join(project_dir, "qibuild.manifest")
    if not os.path.exists(manifest):
        return os.path.basename(project_dir)
    config = qibuild.configstore.ConfigStore()
    conf_file = os.path.join(project_dir, "qibuild.manifest")
    config.read(conf_file)
    project_names = config.get("project", default=dict()).keys()
    if len(project_names) != 1:
        mess  = "The file %s is invalid\n" % conf_file
        mess += "It should contains exactly one project section"
        raise Exception(mess)

    return project_names[0]


def version_from_directory(project_dir):
    """Try to guess version from the sources of the project.

    Return None if not found.
    """
    version_cmake = os.path.join(project_dir, "version.cmake")
    if not os.path.exists(version_cmake):
        return None
    contents = None
    with open(version_cmake, "r") as fp:
        contents = fp.read()
    name = name_from_directory(project_dir)
    import re
    up_name = name.upper()
    match = re.match('^set\(%s_VERSION\s+"?(.*?)"?\s*\)' % up_name,
                     contents)
    if not match:
        LOGGER.warning("Invalid version.cmake. Should have a line looking like\n"
           "set(%s_VERSION <VERSION>)",  up_name)
        return None
    return match.groups()[0]

