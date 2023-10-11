#include "database/grid.h"

#include <iostream>

namespace bitstream
{

    Grid::Grid(const rapidjson::Document &tilegrid)
    {
        for (const auto &tile : tilegrid.GetObject())
        {
            auto tile_name = tile.name.GetString();
            auto tile_type = tile.value["type"].GetString();
            std::map<BlockType, Bits> bits;
            std::map<std::string, std::string> pin_functions;
            std::map<std::string, std::string> sites;
            std::optional<ClockRegion> clock_region;

            for (const auto &function : tile.value["pin_functions"].GetObject())
            {
                sites.emplace(function.name.GetString(), function.value.GetString());
            }

            for (const auto &site : tile.value["sites"].GetObject())
            {
                sites.emplace(site.name.GetString(), site.value.GetString());
            }

            if (tile.value.HasMember("clock_region"))
            {
                clock_region = ClockRegion(tile.value["clock_region"].GetString());
            }

            if (tile.value.HasMember("bits"))
            {
                for (const auto &bit : tile.value["bits"].GetObject())
                {
                    auto block_type = string_to_block_type(bit.name.GetString());
                    u32 base_addr = std::stoi(bit.value["baseaddr"].GetString(), 0, 16);
                    u32 frames = bit.value["frames"].GetUint();
                    u32 offset = bit.value["offset"].GetUint();
                    u32 words = bit.value["words"].GetUint();
                    std::optional<BitAlias> alias;

                    if (bit.value.HasMember("alias"))
                    {
                        auto alias_json = bit.value["alias"].GetObject();
                        auto type = alias_json["type"].GetString();
                        u32 start_offset = alias_json["start_offset"].GetUint();

                        std::map<std::string, std::string> alias_sites;
                        for (const auto &site : alias_json["sites"].GetObject())
                        {
                            alias_sites[site.name.GetString()] = site.value.GetString();
                        }

                        alias = BitAlias(type, alias_sites, start_offset);
                    }

                    bits.emplace(block_type, Bits(base_addr, frames, offset, words, alias));
                }
            }

            auto grid_info = std::make_shared<GridInfo>(GridInfo(tile_name, tile_type, bits, pin_functions, sites, clock_region));
            name_to_grid_info_.emplace(tile_name, grid_info);

            for (const auto &b : grid_info->bits())
            {
                u32 base_address = b.second.base_address();
                frame_address_to_grid_info_[base_address].push_back(grid_info);
            }
        }
    }

    std::vector<std::shared_ptr<GridInfo>> Grid::get_grid_info(u32 frame_address) const
    {
        auto grid_info = (--frame_address_to_grid_info_.upper_bound(frame_address))->second;
        std::vector<std::shared_ptr<GridInfo>> res;

        for (const auto &g : grid_info)
        {
            for (const auto &b : g->bits())
            {
                if (frame_address < (-b.second.base_address() + b.second.frames()))
                {
                    res.push_back(g);
                }
            }
        }

        return res;
    }

    std::shared_ptr<GridInfo> Grid::get_grid_info(const std::string &tile_name) const
    {
        if (const auto &it = name_to_grid_info_.find(tile_name); it != name_to_grid_info_.end())
        {
            return it->second;
        }

        return nullptr;
    }

} // namespace bitstream