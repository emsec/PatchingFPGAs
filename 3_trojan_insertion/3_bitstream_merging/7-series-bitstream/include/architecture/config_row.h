#pragma once

#include "architecture/block_type.h"
#include "architecture/config_bus.h"
#include "architecture/frame_address.h"

#include <yaml-cpp/yaml.h>

#include <algorithm>
#include <cassert>
#include <map>
#include <memory>

namespace bitstream
{

    // TODO documentation
    class ConfigurationRow
    {
    public:
        ConfigurationRow() = default;

        // Construct a row from a range of iterators that yield FrameAddresses.
        // The addresses may be noncontinguous and/or unsorted but all must
        // share the same row half and row components.
        template <typename T>
        ConfigurationRow(T first, T last);

        // Returns true if the provided address falls within a valid range
        // attributed to this row.  Only the block type, column, and minor
        // address components are considerd as the remaining components are
        // outside the scope of a row.
        bool is_valid_frame_address(FrameAddress address) const;

        // Returns the next numerically increasing address within the Row. If
        // the next address would fall outside the Row, no object is returned.
        // If the next address would cross from one block type to another, no
        // object is returned as other rows of the same block type come before
        // other block types numerically.
        std::optional<FrameAddress> get_next_frame_address(FrameAddress address) const;

    private:
        friend struct YAML::convert<ConfigurationRow>;

        std::map<BlockType, ConfigurationBus> configuration_buses_;
    };

    template <typename T>
    ConfigurationRow::ConfigurationRow(T first, T last)
    {
        assert(std::all_of(first, last, [&](const typename T::value_type &addr) {
            return (addr.is_bottom_half() == first->is_bottom_half() && addr.row() == first->row());
        }));

        std::sort(first, last, [](const FrameAddress &lhs, const FrameAddress &rhs) {
            return lhs.block_type() < rhs.block_type();
        });

        for (auto bus_first = first; bus_first != last;)
        {
            auto bus_last = std::upper_bound(bus_first, last, bus_first->block_type(), [](const BlockType &lhs, const FrameAddress &rhs) {
                return lhs < rhs.block_type();
            });

            configuration_buses_.emplace(bus_first->block_type(), std::move(ConfigurationBus(bus_first, bus_last)));
            bus_first = bus_last;
        }
    }

} // namespace bitstream

namespace YAML
{

    template <>
    struct convert<bitstream::ConfigurationRow>
    {
        static Node encode(const bitstream::ConfigurationRow &rhs);
        static bool decode(const Node &node, bitstream::ConfigurationRow &lhs);
    };

} // namespace YAML
