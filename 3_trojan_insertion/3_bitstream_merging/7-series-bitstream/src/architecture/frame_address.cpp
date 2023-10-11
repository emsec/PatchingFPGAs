#include "architecture/frame_address.h"

#include <iomanip>

namespace bitstream
{

    FrameAddress::FrameAddress(BlockType block_type, bool is_bottom_half, u8 row, u16 column, u8 minor)
    {
        m_address.addr = 0;
        m_address.addr_bits.block_type = (unsigned int)block_type;
        m_address.addr_bits.is_bottom_half = is_bottom_half;
        m_address.addr_bits.row = row;
        m_address.addr_bits.column = column;
        m_address.addr_bits.minor = minor;
    }

    BlockType FrameAddress::block_type() const
    {
        return static_cast<BlockType>(m_address.addr_bits.block_type);
    }

    bool FrameAddress::is_bottom_half() const
    {
        return m_address.addr_bits.is_bottom_half;
    }

    u32 FrameAddress::row() const
    {
        return m_address.addr_bits.row;
    }

    u32 FrameAddress::column() const
    {
        return m_address.addr_bits.column;
    }

    u32 FrameAddress::minor() const
    {
        return m_address.addr_bits.minor;
    }

    std::ostream &operator<<(std::ostream &o, const FrameAddress &addr)
    {
        o << "[" << std::hex << std::showbase << std::setw(10)
          << static_cast<u32>(addr) << "] "
          << (addr.is_bottom_half() ? "BOTTOM" : "TOP")
          << " Row=" << std::setw(2) << std::dec
          << static_cast<unsigned int>(addr.row()) << " Column=" << std::setw(2)
          << std::dec << addr.column() << " Minor=" << std::setw(2) << std::dec
          << static_cast<unsigned int>(addr.minor())
          << " Type=" << addr.block_type();
        return o;
    }

} // namespace bitstream

namespace YAML
{

    Node convert<bitstream::FrameAddress>::encode(const bitstream::FrameAddress &rhs)
    {
        Node node;
        node.SetTag("xilinx/xc7series/frame_address");
        node["block_type"] = rhs.block_type();
        node["row_half"] = (rhs.is_bottom_half() ? "bottom" : "top");
        node["row"] = static_cast<unsigned int>(rhs.row());
        node["column"] = static_cast<unsigned int>(rhs.column());
        node["minor"] = static_cast<unsigned int>(rhs.minor());
        return node;
    }

    bool convert<bitstream::FrameAddress>::decode(const Node &node, bitstream::FrameAddress &lhs)
    {
        if (!(node.Tag() == "xilinx/xc7series/frame_address" || node.Tag() == "xilinx/xc7series/configuration_frame_address") ||
            !node["block_type"] || !node["row_half"] || !node["row"] || !node["column"] || !node["minor"])
        {
            return false;
        }

        bool row_half;
        if (node["row_half"].as<std::string>() == "top")
        {
            row_half = false;
        }
        else if (node["row_half"].as<std::string>() == "bottom")
        {
            row_half = true;
        }
        else
        {
            return false;
        }

        lhs = bitstream::FrameAddress(node["block_type"].as<bitstream::BlockType>(), row_half, node["row"].as<unsigned int>(),
                                      node["column"].as<unsigned int>(), node["minor"].as<unsigned int>());
        return true;
    }

} // namespace YAML
