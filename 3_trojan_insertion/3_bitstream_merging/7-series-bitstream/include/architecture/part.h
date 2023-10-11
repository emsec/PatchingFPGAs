#pragma once

#include "architecture/global_clock_region.h"

#include <yaml-cpp/yaml.h>

#include <algorithm>
#include <cstdint>
#include <memory>
#include <optional>
#include <string>
#include <vector>

namespace bitstream
{

    // TODO documentation
    class Part
    {
    public:
        constexpr static u32 kInvalidIdcode = 0;

        static std::shared_ptr<Part> from_file(const std::string &file_path, const std::string &device_type);

        // Constructs an invalid part with a zero IDCODE. Required for YAML
        // conversion but shouldn't be used otherwise.
        Part() : idcode_(kInvalidIdcode) {}

        template <typename T>
        Part(u32 idcode, T collection) : Part(idcode, std::begin(collection), std::end(collection)) {}

        template <typename T>
        Part(u32 idcode, T first, T last);

        u32 idcode() const { return idcode_; }

        std::string device_type() const { return device_type_; }
        std::string device_family() const { return device_family_; }

        bool is_valid_frame_address(FrameAddress address) const;

        std::optional<FrameAddress> get_next_frame_address(FrameAddress address) const;

    private:
        friend struct YAML::convert<Part>;

        u32 idcode_;
        std::string device_type_;
        std::string device_family_;
        GlobalClockRegion top_region_;
        GlobalClockRegion bottom_region_;

        void set_device_type(const std::string &device_type) { device_type_ = device_type; }
        void set_device_family(const std::string &device_family) { device_family_ = device_family; }
    };

    template <typename T>
    Part::Part(u32 idcode, T first, T last) : idcode_(idcode)
    {
        auto first_of_top = std::partition(first, last, [](const FrameAddress &addr) {
            return addr.is_bottom_half();
        });

        top_region_ = GlobalClockRegion(first_of_top, last);
        bottom_region_ = GlobalClockRegion(first, first_of_top);
    }

} // namespace bitstream

namespace YAML
{

    template <>
    struct convert<bitstream::Part>
    {
        static Node encode(const bitstream::Part &rhs);
        static bool decode(const Node &node, bitstream::Part &lhs);
    };

} // namespace YAML