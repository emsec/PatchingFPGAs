#pragma once

#include "architecture/config_column.h"
#include "architecture/frame_address.h"

#include <yaml-cpp/yaml.h>

#include <algorithm>
#include <cassert>
#include <map>
#include <memory>
#include <optional>

namespace bitstream
{

    // TODO documentation
    // ConfigurationBus represents a bus for sending frames to a specific BlockType
    // within a Row.  An instance of ConfigurationBus will contain one or more
    // ConfigurationColumns.
    class ConfigurationBus
    {
    public:
        ConfigurationBus() = default;

        // Constructs a ConfigurationBus from iterators yielding
        // FrameAddresses.  The frame address need not be contiguous or sorted
        // but they must all have the same block type, row half, and row
        // address components.
        template <typename T>
        ConfigurationBus(T first, T last);

        // Returns true if the provided address falls into a valid segment of
        // the address range on this bus.  Only the column and minor components
        // of the address are considered as all other components are outside
        // the scope of a bus.
        bool is_valid_frame_address(FrameAddress address) const;

        // Returns the next valid address on the bus in numerically increasing
        // order. If the next address would fall outside this bus, no object is
        // returned.
        std::optional<FrameAddress> get_next_frame_address(FrameAddress address) const;

    private:
        friend struct YAML::convert<ConfigurationBus>;

        std::map<unsigned int, ConfigurationColumn> configuration_columns_;
    };

    template <typename T>
    ConfigurationBus::ConfigurationBus(T first, T last)
    {
        assert(std::all_of(first, last, [&](const typename T::value_type &addr) {
            return (addr.block_type() == first->block_type() && addr.is_bottom_half() == first->is_bottom_half() && addr.row() == first->row());
        }));

        std::sort(first, last, [](const FrameAddress &lhs, const FrameAddress &rhs) {
            return lhs.column() < rhs.column();
        });

        for (auto col_first = first; col_first != last;)
        {
            auto col_last = std::upper_bound(col_first, last, col_first->column(), [](const unsigned int &lhs, const FrameAddress &rhs) {
                return lhs < rhs.column();
            });

            configuration_columns_.emplace(col_first->column(), std::move(ConfigurationColumn(col_first, col_last)));
            col_first = col_last;
        }
    }

} // namespace bitstream

namespace YAML
{

    template <>
    struct convert<bitstream::ConfigurationBus>
    {
        static Node encode(const bitstream::ConfigurationBus &rhs);
        static bool decode(const Node &node, bitstream::ConfigurationBus &lhs);
    };

} // namespace YAML