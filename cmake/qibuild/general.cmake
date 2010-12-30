##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

#get the current directory of the file
get_filename_component(_ROOT_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)
list(APPEND CMAKE_PREFIX_PATH ${_ROOT_DIR}/modules/)

if(${CMAKE_VERSION} VERSION_LESS 2.8.3)
  list(APPEND CMAKE_MODULE_PATH ${_ROOT_DIR}/extern)
endif()

set(QI_TEMPLATE_DIR ${_ROOT_DIR}/templates)

include("qibuild/log")
include("qibuild/set")
include("qibuild/subdirectory")
include("qibuild/internal/layout")
include("qibuild/internal/check")
include("qibuild/internal/install")
include("qibuild/internal/glob")
include("qibuild/internal/stage")
include("qibuild/internal/autostrap")

if (NOT QI_SDK_DIR)
  qi_set_global(QI_SDK_DIR "${CMAKE_BINARY_DIR}/sdk/")
  qi_info("QI_SDK_DIR: ${QI_SDK_DIR}")
endif (NOT QI_SDK_DIR)

#force buildtype to be Upper case
if (DEFINED CMAKE_BUILD_TYPE)
  string(TOUPPER "${CMAKE_BUILD_TYPE}" "_BUILD_TYPE")
  qi_set_global(CMAKE_BUILD_TYPE "${_BUILD_TYPE}")
endif()

#ensure CMAKE_BUILD_TYPE is either Debug or Release
if (CMAKE_BUILD_TYPE STREQUAL "")
  qi_set_global(CMAKE_BUILD_TYPE "RELEASE")
endif (CMAKE_BUILD_TYPE STREQUAL "")

include("qibuild/find")
include("qibuild/uselib")
include("qibuild/launcher")
include("qibuild/tests")
include("qibuild/install")
include("qibuild/target")
include("qibuild/submodule")
include("qibuild/stage")
include("qibuild/doc")
include("qibuild/autotools")

list(INSERT CMAKE_PREFIX_PATH 0 ${QI_SDK_DIR})

_qi_autostrap_update()
