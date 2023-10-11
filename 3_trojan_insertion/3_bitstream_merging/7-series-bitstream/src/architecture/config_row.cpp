#include "architecture/config_row.h"

namespace bitstream
{

    bool ConfigurationRow::is_valid_frame_address(FrameAddress address) const
    {
        auto addr_bus = configuration_buses_.find(address.block_type());

        if (addr_bus == configuration_buses_.end())
        {
            return false;
        }

        return addr_bus->second.is_valid_frame_address(address);
    }

    std::optional<FrameAddress> ConfigurationRow::get_next_frame_address(FrameAddress address) const
    {
        // find bus of current address
        auto addr_bus = configuration_buses_.find(address.block_type());
        if (addr_bus == configuration_buses_.end())
        {
            return std::nullopt;
        }

        // querry bus for next address
        std::optional<FrameAddress> next_address = addr_bus->second.get_next_frame_address(address);
        if (next_address.has_value())
        {
            return next_address;
        }

        // next address is not part of current bus, so it must be in a different row
        return std::nullopt;
    }

} // namespace bitstream

namespace YAML
{

    Node convert<bitstream::ConfigurationRow>::encode(const bitstream::ConfigurationRow &rhs)
    {
        Node node;
        node.SetTag("xilinx/xc7series/row");
        node["configuration_buses"] = rhs.configuration_buses_;
        return node;
    }

    bool convert<bitstream::ConfigurationRow>::decode(const Node &node, bitstream::ConfigurationRow &lhs)
    {
        if (!node.Tag().empty() && node.Tag() != "xilinx/xc7series/row")
        {
            return false;
        }

        lhs.configuration_buses_ = node["configuration_buses"].as<std::map<bitstream::BlockType, bitstream::ConfigurationBus>>();
        return true;
    }

} // namespace YAML
