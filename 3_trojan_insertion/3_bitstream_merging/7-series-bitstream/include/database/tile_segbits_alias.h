#pragma once

#include "architecture/block_type.h"
#include "database/grid.h"
#include "database/tile_segbits.h"
#include "database/tile_segbits_default.h"
#include "defines.h"

#include <map>
#include <string>
#include <vector>

namespace bitstream
{

    class Database;

    // TODO documentation
    /**
     * Class holding the actual mapping from bits in the bitstream to the actual configuration of a single tile type on the FPGA.
     *
     * The configuration for each tile of the same tile type is equal, such that it only needs to be stored once and can then be
     * placed at the respective positions of the bitsgtream.
     */
    class TileSegbitsAlias : public TileSegbits
    {
    public:
        TileSegbitsAlias(const TileData &tile_db, const std::string &tile_type, const std::map<BlockType, Bits> &bits_map, const std::function<std::shared_ptr<TileSegbits>(std::string)> &get_tile_segbits);

        std::map<std::string, std::vector<std::pair<u32, u32>>> bits_to_features(BlockType block_type, const Bits &bits, const std::map<u32, std::pair<std::set<u32>, std::set<u32>>> &bit_data);
        std::map<BlockType, std::vector<std::pair<Bit, bool>>> features_to_bits(const std::map<BlockType, Bits> &bits, const std::map<std::string, bool> &features);

    private:
        std::string m_tile_type;
        std::map<BlockType, Bits> m_bits_map;
        std::map<BlockType, BitAlias> m_alias;
        std::map<BlockType, Bits> m_alias_bits_map;
        std::string m_alias_tile_type;
        std::map<BlockType, std::map<std::string, std::string>> m_sites_rev_map;
        std::shared_ptr<TileSegbitsDefault> m_tile_segbits;

        std::function<bool(BlockType, const Bit &)> m_filter = [this](BlockType block_type, const Bit &bit) -> bool {
            auto word = bit.word_bit() / 32;
            auto real_word = word - m_alias.at(block_type).start_offset();

            if (real_word < 0 || real_word > m_bits_map.at(block_type).words())
            {
                return false;
            }

            return true;
        };
    };

} // namespace bitstream
