#pragma once

#include <yaml-cpp/yaml.h>

#include <ostream>

namespace bitstream
{

    // TODO documentation
    enum class BlockType : unsigned int
    {
        CLB_IO_CLK = 0x0,
        BLOCK_RAM = 0x1,
        CFG_CLB = 0x2,
        ERROR_TYPE = 0x3,
    };

    BlockType string_to_block_type(const std::string &str);
    std::ostream &operator<<(std::ostream &o, BlockType value);

} // namespace bitstream

namespace YAML
{

    template <>
    struct convert<bitstream::BlockType>
    {
        static Node encode(const bitstream::BlockType rhs);
        static bool decode(const Node &node, bitstream::BlockType &lhs);
    };

} // namespace YAML
