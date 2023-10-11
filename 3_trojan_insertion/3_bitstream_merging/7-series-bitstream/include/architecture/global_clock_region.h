#pragma once

#include "architecture/config_row.h"
#include "architecture/frame_address.h"

#include <yaml-cpp/yaml.h>

#include <algorithm>
#include <cassert>
#include <map>
#include <memory>

namespace bitstream
{

    // TODO documentation
    // GlobalClockRegion represents all the resources associated with a single
    // global clock buffer (BUFG) tile.  In 7-Series FPGAs, there are two BUFG
    // tiles that divide the chip into top and bottom "halves". Each half may
    // contains any number of rows, buses, and columns.
    class GlobalClockRegion
    {
    public:
        GlobalClockRegion() = default;

        // Construct a GlobalClockRegion from iterators that yield
        // FrameAddresses which are known to be valid. The addresses may be
        // noncontinguous and/or unordered but they must share the same row
        // half address component.
        template <typename T>
        GlobalClockRegion(T first, T last);

        // Returns true if the address falls within a valid range inside the
        // global clock region. The row half address component is ignored as it
        // is outside the context of a global clock region.
        bool is_valid_frame_address(FrameAddress address) const;

        // Returns the next numerically increasing address known within this
        // global clock region. If the next address would fall outside this
        // global clock region, no address is returned. If the next address
        // would jump to a different block type, no address is returned as the
        // same block type in other global clock regions come numerically
        // before other block types.
        std::optional<FrameAddress> get_next_frame_address(FrameAddress address) const;

    private:
        friend struct YAML::convert<GlobalClockRegion>;

        std::map<unsigned int, ConfigurationRow> rows_;
    };

    template <typename T>
    GlobalClockRegion::GlobalClockRegion(T first, T last)
    {
        assert(std::all_of(first, last, [&](const typename T::value_type &addr) {
            return addr.is_bottom_half() == first->is_bottom_half();
        }));

        std::sort(first, last, [](const FrameAddress &lhs, const FrameAddress &rhs) {
            return lhs.row() < rhs.row();
        });

        for (auto row_first = first; row_first != last;)
        {
            auto row_last = std::upper_bound(row_first, last, row_first->row(), [](const uint8_t &lhs, const FrameAddress &rhs) {
                return lhs < rhs.row();
            });

            rows_.emplace(row_first->row(), std::move(ConfigurationRow(row_first, row_last)));
            row_first = row_last;
        }
    }

} // namespace bitstream

namespace YAML
{

    template <>
    struct convert<bitstream::GlobalClockRegion>
    {
        static Node encode(const bitstream::GlobalClockRegion &rhs);
        static bool decode(const Node &node, bitstream::GlobalClockRegion &lhs);
    };

} // namespace YAML
