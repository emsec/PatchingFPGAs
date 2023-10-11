#include "database/tile_segbits_alias.h"
#include "utils/utils.h"

#include <cassert>
#include <iostream>

namespace bitstream
{
    TileSegbitsAlias::TileSegbitsAlias(const TileData &tile_db, const std::string &tile_type, const std::map<BlockType, Bits> &bits_map, const std::function<std::shared_ptr<TileSegbits>(std::string)> &get_tile_segbits) : m_tile_type(tile_type), m_bits_map(bits_map)
    {
        for (const auto &[block_type, bit] : m_bits_map)
        {
            if (bit.alias().has_value())
            {
                const auto bit_alias = bit.alias().value();
                m_alias.emplace(block_type, bit_alias);
                m_alias_bits_map.emplace(block_type, Bits(bit.base_address(), bit.frames(), bit.offset() - bit_alias.start_offset(), bit.words(), std::nullopt));

                if (m_alias_tile_type.empty())
                {
                    m_alias_tile_type = bit_alias.type();
                }
                else
                {
                    if (m_alias_tile_type != m_alias.at(block_type).type())
                    {
                        std::cerr << "[ERROR] Tile Segbits Alias: current alias tile type '" << m_alias_tile_type << "' does not match new alias tile type '" << m_alias.at(block_type).type() << "'." << std::endl;
                    }
                }

                for (const auto &site : bit_alias.sites())
                {
                    m_sites_rev_map[block_type].emplace(site.second, site.first);
                }
            }
        }

        if (const auto &ppips = tile_db.ppips(); !ppips.empty())
        {
            // read pseudo PIPs from file
            m_ppips = read_ppips(ppips);
        }

        m_tile_segbits = std::static_pointer_cast<TileSegbitsDefault>(get_tile_segbits(m_alias_tile_type));
    }

    std::map<std::string, std::vector<std::pair<u32, u32>>> TileSegbitsAlias::bits_to_features(BlockType block_type, const Bits &bits, const std::map<u32, std::pair<std::set<u32>, std::set<u32>>> &bit_data)
    {
        std::map<std::string, std::vector<std::pair<u32, u32>>> res;

        if (const auto &it = m_alias_bits_map.find(block_type); it != m_alias_bits_map.end())
        {
            auto alias_bits = m_alias_bits_map.at(block_type);

            for (const auto &[alias_feature, bit_addresses] : m_tile_segbits->bits_to_features(block_type, alias_bits, bit_data, m_filter))
            {
                //  map from alias feature name to final feature name
                auto parts = utils::split(alias_feature, '.');

                if (parts[0] != m_alias_tile_type)
                {
                    std::cerr << "[ERROR] Tile Segbits Alias: first part of feature name '" << parts[0] << "' does not match alias tile type '" << m_alias_tile_type << "'." << std::endl;
                    return {};
                }
                parts[0] = m_tile_type;

                for (const auto &[block_type, site_map] : m_sites_rev_map)
                {
                    if (const auto &it = site_map.find(parts[1]); parts.size() > 1 && it != site_map.end())
                    {
                        parts[1] = site_map.at(parts[1]);
                    }
                }

                res.emplace(utils::join(parts, "."), bit_addresses);
            }
        }

        return res;
    }

    std::map<BlockType, std::vector<std::pair<Bit, bool>>> TileSegbitsAlias::features_to_bits(const std::map<BlockType, Bits> &bits, const std::map<std::string, bool> &features)
    {
        std::map<std::string, bool> alias_features;

        // map features to aliased features
        for (const auto &[feature, is_enabled] : features)
        {
            if (const auto ppip_it = m_ppips.find(feature); ppip_it != m_ppips.end())
            {
                continue;
            }

            auto parts = utils::split(feature, '.');
            parts.at(0) = m_alias_tile_type;

            for (const auto &[block_type, alias] : m_alias)
            {
                if (parts.at(1).size() > 1)
                {
                    const auto &alias_sites = alias.sites();
                    if (const auto alias_it = alias_sites.find(parts.at(1)); alias_it != alias_sites.end())
                    {
                        parts.at(1) = alias_it->second;
                    }
                }
            }

            alias_features.emplace(utils::join(parts, "."), is_enabled);
        }

        return m_tile_segbits->features_to_bits(m_alias_bits_map, alias_features);
    }

} // namespace bitstream
