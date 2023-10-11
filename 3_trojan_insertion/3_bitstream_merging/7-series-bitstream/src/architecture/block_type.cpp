#include "architecture/block_type.h"

namespace bitstream
{

    BlockType string_to_block_type(const std::string &str)
    {
        if (str == "CLB_IO_CLK")
        {
            return BlockType::CLB_IO_CLK;
        }
        else if (str == "BLOCK_RAM")
        {
            return BlockType::BLOCK_RAM;
        }
        else if (str == "CFG_CLB")
        {
            return BlockType::CFG_CLB;
        }
        else
        {
            return BlockType::ERROR_TYPE;
        }
    }

    std::ostream &
    operator<<(std::ostream &o, BlockType value)
    {
        switch (value)
        {
        case BlockType::CLB_IO_CLK:
            o << "CLB/IO/CLK";
            break;
        case BlockType::BLOCK_RAM:
            o << "Block RAM";
            break;
        case BlockType::CFG_CLB:
            o << "Config CLB";
            break;
        case BlockType::ERROR_TYPE:
            o << "ERROR";
            break;
        }

        return o;
    }

} // namespace bitstream

namespace YAML
{

    Node convert<bitstream::BlockType>::encode(const bitstream::BlockType rhs)
    {
        switch (rhs)
        {
        case bitstream::BlockType::CLB_IO_CLK:
            return Node("CLB_IO_CLK");
        case bitstream::BlockType::BLOCK_RAM:
            return Node("BLOCK_RAM");
        case bitstream::BlockType::CFG_CLB:
            return Node("CFG_CLB");
        default:
            return Node(static_cast<unsigned int>(rhs));
        }
    }

    bool YAML::convert<bitstream::BlockType>::decode(const Node &node, bitstream::BlockType &lhs)
    {
        auto type_str = node.as<std::string>();

        if (type_str == "CLB_IO_CLK")
        {
            lhs = bitstream::BlockType::CLB_IO_CLK;
            return true;
        }
        else if (type_str == "BLOCK_RAM")
        {
            lhs = bitstream::BlockType::BLOCK_RAM;
            return true;
        }
        else if (type_str == "CFG_CLB")
        {
            lhs = bitstream::BlockType::CFG_CLB;
            return true;
        }
        else
        {
            return false;
        }
    }

} // namespace YAML
