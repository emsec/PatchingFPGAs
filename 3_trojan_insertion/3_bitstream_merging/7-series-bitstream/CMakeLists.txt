cmake_minimum_required(VERSION 3.16)

project(BitstreamReader
        VERSION 0.1
        DESCRIPTION "Xilinx 7Series Bitstream Reaxder"
        LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 17)


add_subdirectory(extern/gflags)
add_subdirectory(extern/yaml-cpp)

include(ExternalProject)
include("${CMAKE_SOURCE_DIR}/extern/rapidjson.cmake")

file(GLOB_RECURSE BITSTREAM_HDR ${CMAKE_CURRENT_SOURCE_DIR}/include/*.h)
file(GLOB_RECURSE BITSTREAM_SRC ${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp)

include_directories(${RAPIDJSON_INCLUDE_DIR})

# SET(CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} -fsanitize=address")

add_library(bitstreamlib STATIC ${BITSTREAM_HDR} ${BITSTREAM_SRC})
target_include_directories(bitstreamlib PUBLIC include)
target_link_libraries(bitstreamlib PUBLIC yaml-cpp::yaml-cpp)
add_dependencies(bitstreamlib rapidjson)

add_subdirectory(app)
