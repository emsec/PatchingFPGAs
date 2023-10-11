#include "architecture/config_bus.h"

namespace bitstream
{

    bool ConfigurationBus::is_valid_frame_address(FrameAddress address) const
    {
        auto addr_column = configuration_columns_.find(address.column());

        if (addr_column == configuration_columns_.end())
        {
            return false;
        }

        return addr_column->second.is_valid_frame_address(address);
    }

    std::optional<FrameAddress> ConfigurationBus::get_next_frame_address(FrameAddress address) const
    {
        // find column of current address
        auto addr_column = configuration_columns_.find(address.column());
        if (addr_column == configuration_columns_.end())
        {
            return std::nullopt;
        }

        // querry column for next address
        std::optional<FrameAddress> next_address = addr_column->second.get_next_frame_address(address);
        if (next_address.has_value())
        {
            return next_address;
        }

        // next address is not part of current column, so it must be first frame of next column
        if (++addr_column != configuration_columns_.end())
        {
            auto next_address = FrameAddress(address.block_type(), address.is_bottom_half(), address.row(), addr_column->first, 0);

            if (addr_column->second.is_valid_frame_address(next_address))
            {
                return next_address;
            }
        }

        // next address is not part of this bus, so it must be in a different bus
        return std::nullopt;
    }

} // namespace bitstream

namespace YAML
{

    Node convert<bitstream::ConfigurationBus>::encode(const bitstream::ConfigurationBus &rhs)
    {
        Node node;

        node.SetTag("xilinx/xc7series/configuration_bus");
        node["configuration_columns"] = rhs.configuration_columns_;

        return node;
    }

    bool convert<bitstream::ConfigurationBus>::decode(const Node &node, bitstream::ConfigurationBus &lhs)
    {
        if (!node.Tag().empty() && node.Tag() != "xilinx/xc7series/configuration_bus")
        {
            return false;
        }

        lhs.configuration_columns_ = node["configuration_columns"].as<std::map<unsigned int, bitstream::ConfigurationColumn>>();
        return true;
    }

} // namespace YAML
