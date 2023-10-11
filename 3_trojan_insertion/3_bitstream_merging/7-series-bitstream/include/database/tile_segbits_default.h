#pragma once

#include "architecture/block_type.h"
#include "database/tile_segbits.h"
#include "defines.h"

#include <map>
#include <string>
#include <vector>

namespace bitstream
{

    // TODO documentation
    /**
     * Class holding the actual mapping from bits in the bitstream to the actual configuration of a single tile type on the FPGA.
     * 
     * The configuration for each tile of the same tile type is equal, such that it only needs to be stored once and can then be
     * placed at the respective positions of the bitsgtream.
     */
    class TileSegbitsDefault : public TileSegbits
    {
    public:
        /**
         * Constructor for a TileSegbitsDefault object.
         *
         * @param[in] tile_db - TileData instance holding the paths to the files relevant for a single tile type.
         */
        TileSegbitsDefault(const TileData &tile_db);

        std::map<std::string, std::vector<std::pair<u32, u32>>> bits_to_features(BlockType block_type, const Bits &bits, const std::map<u32, std::pair<std::set<u32>, std::set<u32>>> &bit_data);
        std::map<std::string, std::vector<std::pair<u32, u32>>> bits_to_features(BlockType block_type, const Bits &bits, const std::map<u32, std::pair<std::set<u32>, std::set<u32>>> &bit_data, const std::function<bool(BlockType, const Bit &)> &filter);
        std::map<BlockType, std::vector<std::pair<Bit, bool>>> features_to_bits(const std::map<BlockType, Bits> &bits, const std::map<std::string, bool> &features);

    private:
        std::map<BlockType, std::map<std::string, std::vector<Bit>>> m_segbits;
        std::map<std::string, std::map<u32, std::pair<BlockType, std::string>>> m_feature_addresses;

        std::map<std::string, std::vector<Bit>> read_segbits(const std::string &file_path);
        Bit parse_bit(const std::string &bits_str);
    };

} // namespace bitstream