#pragma once

#include "architecture/frame_address.h"
#include "defines.h"

#include <rapidjson/document.h>

#include <iostream>
#include <map>
#include <optional>
#include <regex>
#include <string>

namespace bitstream
{

    // TODO documentation
    struct BitAlias
    {
    public:
        BitAlias(const std::string &type, const std::map<std::string, std::string> &sites, u32 start_offset) : type_(type), sites_(sites), start_offset_(start_offset) {}

        std::string type() const { return type_; }
        std::map<std::string, std::string> sites() const { return sites_; }
        u32 start_offset() const { return start_offset_; }

    private:
        std::string type_;
        std::map<std::string, std::string> sites_;
        u32 start_offset_;
    };

    struct Bits
    {
    public:
        Bits(u32 base_address, u32 frames, u32 offset, u32 words, const std::optional<BitAlias> &alias) : base_address_(base_address), frames_(frames), offset_(offset), words_(words), alias_(alias) {}

        u32 base_address() const { return base_address_; }
        u32 frames() const { return frames_; }
        u32 offset() const { return offset_; }
        u32 words() const { return words_; }
        std::optional<BitAlias> alias() const { return alias_; }

    private:
        // base frame address
        u32 base_address_;

        // number of frames
        u32 frames_;

        // offset in words
        u32 offset_;

        // number of words
        u32 words_;

        std::optional<BitAlias> alias_;
    };

    struct ClockRegion
    {
    public:
        ClockRegion(const std::string &name) : name_(name)
        {
            static std::regex clk_reg("X([0-9]+)Y([0-9]+)");
            std::smatch sm;
            std::regex_match(name, sm, clk_reg);
            x_ = std::stoi(sm[1]);
            y_ = std::stoi(sm[2]);
        }

        std::string name() const { return name_; }
        u32 x() const { return x_; }
        u32 y() const { return y_; }

    private:
        std::string name_;
        u32 x_;
        u32 y_;
    };

    struct GridInfo
    {
    public:
        GridInfo(const std::string &name, const std::string &type, const std::map<BlockType, Bits> &bits, const std::map<std::string, std::string> &pin_functions, const std::map<std::string, std::string> &sites, const std::optional<ClockRegion> &clock_region) : name_(name), type_(type), bits_(bits), pin_functions_(pin_functions), sites_(sites), clock_region_(clock_region) {}

        std::string name() const { return name_; }
        std::string type() const { return type_; }
        std::map<BlockType, Bits> bits() const { return bits_; }
        std::map<std::string, std::string> pin_functions() const { return pin_functions_; }
        std::map<std::string, std::string> sites() const { return sites_; }
        std::optional<ClockRegion> clock_region() const { return clock_region_; }

    private:
        std::string name_;
        std::string type_;
        std::map<BlockType, Bits> bits_;
        std::map<std::string, std::string> pin_functions_;
        std::map<std::string, std::string> sites_;
        std::optional<ClockRegion> clock_region_;
    };

    class Grid
    {
    public:
        Grid() = default;
        Grid(const rapidjson::Document &tilegrid);
        std::vector<std::shared_ptr<GridInfo>> get_grid_info(u32 frame_address) const;
        std::shared_ptr<GridInfo> get_grid_info(const std::string &tile_name) const;

    private:
        std::map<std::string, std::shared_ptr<GridInfo>> name_to_grid_info_;
        std::map<u32, std::vector<std::shared_ptr<GridInfo>>> frame_address_to_grid_info_;
    };

} // namespace bitstream
