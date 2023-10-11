#include "architecture/global_clock_region.h"

namespace bitstream
{

    bool GlobalClockRegion::is_valid_frame_address(FrameAddress address) const
    {
        auto addr_row = rows_.find(address.row());
        if (addr_row == rows_.end())
            return false;
        return addr_row->second.is_valid_frame_address(address);
    }

    std::optional<FrameAddress> GlobalClockRegion::get_next_frame_address(FrameAddress address) const
    {
        // find row of current address
        auto addr_row = rows_.find(address.row());
        if (addr_row == rows_.end())
        {
            return std::nullopt;
        }

        // querry row for next address
        std::optional<FrameAddress> next_address = addr_row->second.get_next_frame_address(address);
        if (next_address.has_value())
        {
            return next_address;
        }

        // next address is not part of current row, so it must be first frame of next row
        if (++addr_row != rows_.end())
        {
            auto next_address = FrameAddress(address.block_type(), address.is_bottom_half(), addr_row->first, 0, 0);
            if (addr_row->second.is_valid_frame_address(next_address))
            {
                return next_address;
            }
        }

        // next address is not part of this row, so it must be in a different global clock region
        return std::nullopt;
    }

} // namespace bitstream

namespace YAML
{

    Node convert<bitstream::GlobalClockRegion>::encode(const bitstream::GlobalClockRegion &rhs)
    {
        Node node;
        node.SetTag("xilinx/xc7series/global_clock_region");
        node["rows"] = rhs.rows_;
        return node;
    }

    bool convert<bitstream::GlobalClockRegion>::decode(const Node &node, bitstream::GlobalClockRegion &lhs)
    {
        if (!node.Tag().empty() && node.Tag() != "xilinx/xc7series/global_clock_region")
        {
            return false;
        }

        lhs.rows_ = node["rows"].as<std::map<unsigned int, bitstream::ConfigurationRow>>();
        return true;
    }

} // namespace YAML
