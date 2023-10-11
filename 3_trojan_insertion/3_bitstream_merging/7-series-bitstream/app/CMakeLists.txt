add_executable(bitstream reader.cpp)
target_link_libraries(bitstream PRIVATE bitstreamlib gflags::gflags yaml-cpp::yaml-cpp)