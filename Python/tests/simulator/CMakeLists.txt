cmake_minimum_required (VERSION 2.8.11)
project (simulator)

set (CCLIB_DIR ${PROJECT_SOURCE_DIR}/../../../Arduino/CCLib)
include_directories( ${CCLIB_DIR} )
include_directories( ${PROJECT_SOURCE_DIR}/emulated )

file ( GLOB WEBAPI_SOURCES
  ${PROJECT_SOURCE_DIR}/*.cpp
  ${PROJECT_SOURCE_DIR}/emulated/*.cpp
  ${CCLIB_DIR}/*.cpp
)

add_executable (simulator ${WEBAPI_SOURCES})
