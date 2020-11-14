cmake_minimum_required(VERSION 3.0)
set(TARGET_NAME ov_mlperf)
project(${TARGET_NAME})

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIE -fstack-protector-strong -Wno-error")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC -fno-operator-names -Wformat -Wformat-security -Wall -O2")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14 -pthread -USE_OPENCV -DBOOST_ERROR_CODE_HEADER_ONLY")
if (OPENVINO_VER STREQUAL "2019_R3.1" OR OPENVINO_VER STREQUAL "2019_R3" OR OPENVINO_VER STREQUAL "pre-release")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DBUILD_2019")
endif()

set(CMAKE_BUILD_TYPE "Release")

if (CMAKE_BUILD_TYPE STREQUAL "")
    message(STATUS "CMAKE_BUILD_TYPE not defined, 'Release' will be used")
    set(CMAKE_BUILD_TYPE "Release")
endif()

if (NOT(BUILD_DIR))
    MESSAGE(STATUS "BUILD_DIR not defined. Will build to current directory")
    set(BUILD_DIR ${CMAKE_CURRENT_SOURCE_DIR})
endif()

if (NOT(BIN_FOLDER))
    set(BIN_FOLDER ${BUILD_DIR}/${CMAKE_BUILD_TYPE})
else()
    set(BIN_FOLDER ${BUILD_DIR}/${CMAKE_BUILD_TYPE}_${BIN_FOLDER})
endif()

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${BIN_FOLDER})

# OpenCV lib.
if (NOT(OPENCV_DIR))
    MESSAGE(FATAL_ERROR "OPENCV_DIR unspecified. Use -DOPENCV_DIR=/path/to/ck/opencv")
endif()
MESSAGE(STATUS "OPENCV_DIR=${OPENCV_DIR}")
find_package(OpenCV REQUIRED PATHS ${OPENCV_DIR} NO_DEFAULT_PATH)

# OpenVINO Inference Engine.
if (NOT(OPENVINO_DIR))
    MESSAGE(FATAL_ERROR "OPENVINO_DIR unspecified. Use -DOPENVINO_DIR=/path/to/ck/openvino")
endif()
set(OPENVINO_DIR                   "${OPENVINO_DIR}")
set(OPENVINO_LIB_DIR               "${OPENVINO_DIR}/lib")
set(OPENVINO_LIBRARY               "${OPENVINO_LIB_DIR}/libinference_engine.so")
if (OPENVINO_VER STREQUAL "2019_R3.1" OR OPENVINO_VER STREQUAL "2019_R3" OR OPENVINO_VER STREQUAL "pre-release")
  set(OPENVINO_CPU_EXTENSION_LIBRARY "${OPENVINO_LIB_DIR}/libcpu_extension.so")
elseif(OPENVINO_VER STREQUAL "2020" OR OPENVINO_VER STREQUAL "2020.2")
  set(OPENVINO_LEGACY_LIBRARY "${OPENVINO_LIB_DIR}/libinference_engine_legacy.so")
endif()
set(OPENVINO_INCLUDE_DIR           "${OPENVINO_DIR}/include")
set(OPENVINO_EXTENSION_DIR         "${OPENVINO_DIR}/openvino/inference-engine/src/extension")

MESSAGE(STATUS "OPENVINO_DIR=${OPENVINO_DIR}")
MESSAGE(STATUS "OPENVINO_LIB_DIR=${OPENVINO_LIB_DIR}")
MESSAGE(STATUS "OPENVINO_LIBRARY=${OPENVINO_LIBRARY}")
if (OPENVINO_VER STREQUAL "2019_R3.1" OR OPENVINO_VER STREQUAL "2019_R3" OR OPENVINO_VER STREQUAL "pre-release")
  MESSAGE(STATUS "OPENVINO_CPU_EXTENSION_LIBRARY=${OPENVINO_CPU_EXTENSION_LIBRARY}")
elseif(OPENVINO_VER STREQUAL "2020" OR OPENVINO_VER STREQUAL "2020.2")
  MESSAGE(STATUS "OPENVINO_LEGACY_LIBRARY=${OPENVINO_LEGACY_LIBRARY}")
endif()
MESSAGE(STATUS "OPENVINO_INCLUDE_DIR=${OPENVINO_INCLUDE_DIR}")
MESSAGE(STATUS "OPENVINO_EXTENSION_DIR=${OPENVINO_EXTENSION_DIR}")

# MLPerf LoadGen lib.
if (NOT(LOADGEN_DIR))
    MESSAGE(FATAL_ERROR "LOADGEN_DIR unspecified. Use -DLOADGEN_DIR=/path/to/ck/loadgen")
endif()
if (NOT(LOADGEN_LIB_DIR))
    set(LOADGEN_LIB_DIR ${LOADGEN_DIR})
    message(STATUS "LOADGEN_LIB_DIR unspecified. Set to ${LOADGEN_DIR}.")
endif()
message(STATUS "LOADGEN_DIR=${LOADGEN_DIR}")
message(STATUS "LOADGEN_LIB_DIR=${LOADGEN_LIB_DIR}")

find_library(LOADGEN_LIBRARY NAMES mlperf_loadgen PATHS "${LOADGEN_LIB_DIR}/")
if (LOADGEN_LIBRARY_NOTFOUND)
    MESSAGE(FATAL_ERROR "LoadGen library (libmlperf_loadgen.a) not found in ${LOADGEN_LIB_DIR}!")
endif()
message(STATUS "LOADGEN_LIBRARY Found: ${LOADGEN_LIBRARY}" )

# Boost C++ libs.
if (NOT(BOOST_DIR))
    MESSAGE(FATAL_ERROR "BOOST_DIR unspecified. Use -DBOOST_DIR=/path/to/ck/boost")
endif()
set(BOOST_SYSTEM_LIB  "${BOOST_DIR}/lib/libboost_system.so")
set(BOOST_INCLUDE_DIR "${BOOST_DIR}/include")
MESSAGE(STATUS "BOOST_SYSTEM_LIB=${BOOST_SYSTEM_LIB}")
MESSAGE(STATUS "BOOST_INCLUDE_DIR=${BOOST_INCLUDE_DIR}")

# Include directories.
include_directories(
    ${OpenCV_INCLUDE_DIRS}
    ${BOOST_INCLUDE_DIR}
    ${LOADGEN_DIR}
    ${OPENVINO_INCLUDE_DIR}
    ${OPENVINO_EXTENSION_DIR}
)

set(SOURCE_FILES backend_ov.h dataset_ov.h sut_ov.h infer_request_wrap.h item_ov.h main_ov.cc)
add_executable(${TARGET_NAME} ${SOURCE_FILES})

# Link libraries.
target_link_libraries(${TARGET_NAME}
    ${OpenCV_LIBS}
    ${BOOST_SYSTEM_LIB}
    ${LOADGEN_LIBRARY}
    ${OPENVINO_LIBRARY}
    ${OPENVINO_LEGACY_LIBRARY}
    ${OPENVINO_CPU_EXTENSION_LIBRARY}
)
