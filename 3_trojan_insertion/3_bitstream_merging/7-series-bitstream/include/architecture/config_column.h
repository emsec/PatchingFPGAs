#pragma once

#include "architecture/frame_address.h"

#include <yaml-cpp/yaml.h>

#include <algorithm>
#include <cassert>
#include <optional>

namespace bitstream
{

    // TODO documentation
    // ConfigurationColumn represents an endpoint on a ConfigurationBus.
    class ConfigurationColumn
    {
    public:
        ConfigurationColumn() = default;
        ConfigurationColumn(unsigned int frame_count) : frame_count_(frame_count) {}

        // Returns a ConfigurationColumn that describes a continguous range of
        // minor addresses that encompasses the given
        // FrameAddresses.  The provided addresses must only
        // differ only by their minor addresses.
        template <typename T>
        ConfigurationColumn(T first, T last);

        // Returns true if the minor field of the address is within the valid
        // range of this column.
        bool is_valid_frame_address(FrameAddress address) const;

        // Returns the next address in numerical order.  If the next address
        // would be outside this column, return no object.
        std::optional<FrameAddress> get_next_frame_address(FrameAddress address) const;

    private:
        friend struct YAML::convert<ConfigurationColumn>;

        unsigned int frame_count_;
    };

    template <typename T>
    ConfigurationColumn::ConfigurationColumn(T first, T last)
    {
        assert(std::all_of(first, last, [&](const typename T::value_type &addr) {
            return (addr.block_type() == first->block_type() && addr.is_bottom_half() == first->is_bottom_half() && addr.row() == first->row() && addr.column() == first->column());
        }));

        auto max_minor = std::max_element(first, last, [](const FrameAddress &lhs, const FrameAddress &rhs) {
            return lhs.minor() < rhs.minor();
        });

        frame_count_ = max_minor->minor() + 1;
    }

} // namespace bitstream

namespace YAML
{

    template <>
    struct convert<bitstream::ConfigurationColumn>
    {
        static Node encode(const bitstream::ConfigurationColumn &rhs);
        static bool decode(const Node &node, bitstream::ConfigurationColumn &lhs);
    };

} // namespace YAML
