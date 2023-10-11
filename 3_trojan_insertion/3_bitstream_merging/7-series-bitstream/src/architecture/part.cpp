#include "architecture/part.h"
#include "architecture/frame_address.h"
#include "defines.h"

#include <iomanip>
#include <iostream>
#include <sstream>
#include <vector>

namespace bitstream {

std::shared_ptr<Part> Part::from_file(const std::string& file_path, const std::string& device_type)
{
    try {
        YAML::Node yaml = YAML::LoadFile(file_path);
        auto part = yaml.as<Part>();
        part.set_device_type(device_type);

        std::string family = device_type.substr(0, device_type.find("t") + 1);

        // exception; if xc7a35t, change to xc7a50t, because they are the same
        if (family == "xc7a35t") {
            family = "xc7a50t";
        }

        part.set_device_family(family);

        std::cout << "[INFO] Part: successfully read part (" << device_type << " - family: " << family << ") information from file '" << file_path << "'." << std::endl;

        return std::make_shared<Part>(part);
    } catch (YAML::Exception& e) {
        std::cerr << "[ERROR] Part: could not read from file at '" << file_path << "'." << std::endl;
        return nullptr;
    }
}

bool Part::is_valid_frame_address(FrameAddress address) const
{
    if (address.is_bottom_half()) {
        return bottom_region_.is_valid_frame_address(address);
    } else {
        return top_region_.is_valid_frame_address(address);
    }
}

std::optional<FrameAddress> Part::get_next_frame_address(FrameAddress address) const
{
    // querry current global clock region for next address first
    std::optional<FrameAddress> next_address = (address.is_bottom_half() ? bottom_region_.get_next_frame_address(address) : top_region_.get_next_frame_address(address));
    if (next_address) {
        return next_address;
    }

    // if current region is top region, querry bottom region for next address next
    if (!address.is_bottom_half()) {
        next_address = FrameAddress(address.block_type(), true, 0, 0, 0);
        if (bottom_region_.is_valid_frame_address(*next_address)) {
            return next_address;
        }
    }

    // query block type if no match otherwise
    if (address.block_type() < BlockType::BLOCK_RAM) {
        next_address = FrameAddress(BlockType::BLOCK_RAM, false, 0, 0, 0);
        if (is_valid_frame_address(*next_address)) {
            return next_address;
        }
    }

    if (address.block_type() < BlockType::CFG_CLB) {
        next_address = FrameAddress(BlockType::CFG_CLB, false, 0, 0, 0);
        if (is_valid_frame_address(*next_address)) {
            return next_address;
        }
    }

    return std::nullopt;
}

} // namespace bitstream

namespace YAML {

Node convert<bitstream::Part>::encode(const bitstream::Part& rhs)
{
    Node node;
    node.SetTag("xilinx/xc7series/part");

    std::ostringstream idcode_str;
    idcode_str << "0x" << std::hex << rhs.idcode_;
    node["idcode"] = idcode_str.str();
    node["global_clock_regions"]["top"] = rhs.top_region_;
    node["global_clock_regions"]["bottom"] = rhs.bottom_region_;
    return node;
}

bool convert<bitstream::Part>::decode(const Node& node, bitstream::Part& lhs)
{
    if (!node.Tag().empty() && node.Tag() != "xilinx/xc7series/part") {
        return false;
    }

    if (!node["global_clock_regions"] && !node["configuration_ranges"]) {
        return false;
    }

    lhs.idcode_ = node["idcode"].as<uint32_t>();

    if (node["global_clock_regions"]) {
        lhs.top_region_ = node["global_clock_regions"]["top"].as<bitstream::GlobalClockRegion>();
        lhs.bottom_region_ = node["global_clock_regions"]["bottom"].as<bitstream::GlobalClockRegion>();
    } else if (node["configuration_ranges"]) {
        std::vector<bitstream::FrameAddress> addresses;

        for (auto range : node["configuration_ranges"]) {
            auto begin = range["begin"].as<bitstream::FrameAddress>();
            auto end = range["end"].as<bitstream::FrameAddress>();

            for (uint32_t cur = begin; cur < end; ++cur) {
                addresses.push_back(cur);
            }
        }

        lhs = bitstream::Part(lhs.idcode_, addresses);
    }

    return true;
}

} // namespace YAML