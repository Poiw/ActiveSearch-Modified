cmake_minimum_required (VERSION 3.0)

IF (1)
  IF (CMAKE_SYSTEM_PROCESSOR MATCHES "(arm64)|(ARM64)|(aarch64)|(AARCH64)")
    add_definitions (-march=armv8-a)
  ELSEIF (CMAKE_SYSTEM_PROCESSOR MATCHES
          "(arm)|(ARM)|(armhf)|(ARMHF)|(armel)|(ARMEL)")
    add_definitions (-march=armv7-a)
  ELSE ()
    add_definitions (-march=native) #TODO use correct c++11 def once everybody has moved to gcc 4.7 # for now I even removed std=gnu++0x
  ENDIF()
  add_definitions (
    -O3
    -Wall
    -Wextra
    #-Werror
    -Wwrite-strings
    -Wno-unused-parameter
    -fno-strict-aliasing
  )
ENDIF()

if (EXISTS "${CMAKE_SOURCE_DIR}/cmake")
  set (CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_SOURCE_DIR}/cmake)
endif ()

add_subdirectory (examples)
