#include "assembler/disassembler.h"

#include <iostream>

namespace bitstream
{

    Disassembler::Disassembler(std::shared_ptr<Database> db) : m_db(db) { m_grid = m_db->get_grid(); }

    bool Disassembler::add_configuration_to_features(std::shared_ptr<Configuration> config, std::shared_ptr<FASM> fasm_file)
    {
        auto bit_data = config->get_set_bits();
        std::map<std::string, BlockType> checked_tiles;

        // iterate frames
        for (const auto &[frame_address, set_bits] : bit_data)
        {
            // iterate all tiles associated with given frame address
            for (auto grid_info : m_grid->get_grid_info(frame_address))
            {
                for (const auto &[block_type, bits] : grid_info->bits())
                {
                    auto tile_name = grid_info->name();

                    // skip previously checked tiles
                    if (const auto it = checked_tiles.find(tile_name); it != checked_tiles.end() && it->second == block_type)
                    {
                        continue;
                    }

                    // frame contains any data relevant data for tile?
                    bool match = false;
                    for (u32 i = 0; i < bits.words(); i++)
                    {
                        if (const auto &it = set_bits.first.find(i + bits.offset()); it != set_bits.first.end())
                        {
                            match = true;
                        }
                    }

                    if (!match)
                    {
                        continue;
                    }

                    checked_tiles.emplace(tile_name, block_type);
                    auto tile_segbits = m_db->get_tile_segbits(tile_name);
                    if (tile_segbits == nullptr)
                    {
                        // error printed in subfunction
                        continue;
                    }

                    for (const auto &[feature, matched_bits] : tile_segbits->bits_to_features(block_type, bits, bit_data))
                    {
                        fasm_file->add_fasm_line(tile_name, feature);
                    }
                }
            }
        }

        std::cout << "[INFO] Disassembler: Successfully disassembled configuration." << std::endl;
        return true;
    }

} // namespace bitstream