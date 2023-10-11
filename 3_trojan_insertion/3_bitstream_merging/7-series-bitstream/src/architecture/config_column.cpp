#include "architecture/config_column.h"

namespace bitstream
{

    bool ConfigurationColumn::is_valid_frame_address(FrameAddress address) const
    {
        return address.minor() < frame_count_;
    }

    std::optional<FrameAddress> ConfigurationColumn::get_next_frame_address(FrameAddress address) const
    {
        if (!is_valid_frame_address(address))
        {
            return std::nullopt;
        }

        // compute next frame address
        if (static_cast<unsigned int>(address.minor() + 1) < frame_count_)
        {
            return address + 1;
        }

        // next address is not part of this column, so it must be in a different column
        return std::nullopt;
    }

} // namespace bitstream

namespace YAML
{

    Node convert<bitstream::ConfigurationColumn>::encode(const bitstream::ConfigurationColumn &rhs)
    {
        Node node;

        node.SetTag("xilinx/xc7series/configuration_column");
        node["frame_count"] = rhs.frame_count_;

        return node;
    }

    bool convert<bitstream::ConfigurationColumn>::decode(const Node &node, bitstream::ConfigurationColumn &lhs)
    {
        if (!node.Tag().empty() && node.Tag() != "xilinx/xc7series/configuration_column")
        {
            return false;
        }

        lhs.frame_count_ = node["frame_count"].as<unsigned int>();

        return true;
    }

} // namespace YAML
