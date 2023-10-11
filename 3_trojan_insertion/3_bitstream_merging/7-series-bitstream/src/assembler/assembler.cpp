#include "assembler/assembler.h"

#include <iostream>

namespace bitstream
{

    Assembler::Assembler(std::shared_ptr<Database> db) : m_db(db) { m_grid = m_db->get_grid(); }

    bool Assembler::add_features_to_configuration(std::shared_ptr<Configuration> config, std::shared_ptr<FASM> fasm_file)
    {
        // iterate all features denoted in FASM file
        for (const auto &[tile_name, features] : fasm_file->get_features())
        {
            std::map<std::string, bool> db_features;

            auto grid_info = m_grid->get_grid_info(tile_name);
            auto tile_type = grid_info->type();
            auto tile_segbits = m_db->get_tile_segbits(tile_name);

            // construct features as used by database
            for (const auto &[feature, is_enabled] : features)
            {
                db_features.emplace(tile_type + "." + feature, is_enabled);
            }

            for (const auto &[block_type, bits] : tile_segbits->features_to_bits(grid_info->bits(), db_features))
            {
                for (const auto &[bit, is_enabled] : bits)
                {
                    auto frame_addr = bit.word_column();
                    auto word_addr = bit.word_bit() >> 5;
                    auto bit_index = bit.word_bit() & 0x1F;

                    config->set_bit(frame_addr, word_addr, bit_index, bit.is_set() == is_enabled);
                }
            }
        }

        std::cout << "[INFO] Assembler: Successfully assembled configuration." << std::endl;
        return true;
    }

} // namespace bitstream