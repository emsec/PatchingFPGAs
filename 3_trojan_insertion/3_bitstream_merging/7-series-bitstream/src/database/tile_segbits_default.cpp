#include "database/tile_segbits_default.h"
#include "utils/utils.h"

#include <fstream>
#include <iostream>

namespace bitstream
{

    TileSegbitsDefault::TileSegbitsDefault(const TileData &tile_db)
    {
        if (const auto &segbits = tile_db.segbits_clb_io_clk(); !segbits.empty())
        {
            // read segbits of block type CLB_IO_CLK from file
            m_segbits[BlockType::CLB_IO_CLK] = read_segbits(segbits);
        }

        if (const auto &segbits = tile_db.segbits_bram(); !segbits.empty())
        {
            // read segbits of block type BLOCK_RAM from file
            m_segbits[BlockType::BLOCK_RAM] = read_segbits(segbits);
        }

        if (const auto &ppips = tile_db.ppips(); !ppips.empty())
        {
            // read pseudo PIPs from file
            m_ppips = read_ppips(ppips);
        }

        // handle features defined by multiple bits
        for (const auto &[block_type, segbits] : m_segbits)
        {
            for (const auto &feature : segbits)
            {
                auto start_index = feature.first.rfind('[');
                auto end_index = feature.first.rfind(']');

                if (start_index != std::string::npos && end_index != std::string::npos)
                {
                    auto base_feature = feature.first.substr(0, start_index);
                    auto index = std::stoul(feature.first.substr(start_index + 1, end_index - start_index - 1));

                    m_feature_addresses[base_feature].emplace(index, std::make_pair(block_type, feature.first));
                }
            }
        }
    }

    std::map<std::string, std::vector<std::pair<u32, u32>>> TileSegbitsDefault::bits_to_features(BlockType block_type, const Bits &bits, const std::map<u32, std::pair<std::set<u32>, std::set<u32>>> &bit_data)
    {
        return bits_to_features(block_type, bits, bit_data, nullptr);
    }

    std::map<std::string, std::vector<std::pair<u32, u32>>> TileSegbitsDefault::bits_to_features(BlockType block_type, const Bits &bits, const std::map<u32, std::pair<std::set<u32>, std::set<u32>>> &bit_data, const std::function<bool(BlockType, const Bit &)> &filter)
    {
        const auto &segbits_it = m_segbits.find(block_type);
        if (segbits_it == m_segbits.end())
        {
            return {};
        }

        std::map<std::string, std::vector<std::pair<u32, u32>>> res;

        for (const auto &[feature, segbit] : segbits_it->second)
        {
            bool match = true;
            bool skip = false;

            for (const auto &bit : segbit)
            {
                if (filter != nullptr && !filter(block_type, bit))
                {
                    skip = true;
                    break;
                }

                u32 frame_address = bits.base_address() + bit.word_column();
                u32 bit_offset = bits.offset() * 32 + bit.word_bit();

                // is frame_address in relevant bits?
                const auto &frame_it = bit_data.find(frame_address);
                if (frame_it == bit_data.end())
                {
                    // if not, is bit set?
                    match = !(bit.is_set());
                    if (match)
                    {
                        continue;
                    }
                    else
                    {
                        break;
                    }
                }

                const auto &bit_offsets = frame_it->second.second;
                match = (bit_offsets.find(bit_offset) != bit_offsets.end()) == bit.is_set();

                if (!match)
                {
                    break;
                }
            }

            if (!match || skip)
            {
                continue;
            }

            std::vector<std::pair<u32, u32>> bit_addresses;

            for (const auto &bit : segbit)
            {
                if (bit.is_set())
                {
                    u32 frame_address = bits.base_address() + bit.word_column();
                    u32 bit_offset = bits.offset() * 32 + bit.word_bit();

                    bit_addresses.emplace_back(frame_address, bit_offset);
                }
            }

            res.emplace(feature, bit_addresses);
        }

        return res;
    }

    std::map<BlockType, std::vector<std::pair<Bit, bool>>> TileSegbitsDefault::features_to_bits(const std::map<BlockType, Bits> &bits, const std::map<std::string, bool> &features)
    {
        std::map<BlockType, std::vector<std::pair<Bit, bool>>> res;

        for (const auto &[feature, is_enabled] : features)
        {
            if (const auto ppip_it = m_ppips.find(feature); ppip_it != m_ppips.end())
            {
                continue;
            }

            for (const auto &[block_type, features_to_bits_map] : m_segbits)
            {
                if (const auto feature_it = features_to_bits_map.find(feature); feature_it != features_to_bits_map.end())
                {
                    for (const auto &bit : feature_it->second)
                    {
                        u32 word_column = bits.at(block_type).base_address() + bit.word_column();
                        u32 word_bit = bits.at(block_type).offset() * 32 + bit.word_bit();

                        res[block_type].emplace_back(Bit(word_column, word_bit, bit.is_set()), is_enabled);
                    }
                }
            }
        }

        return res;
    }

    std::map<std::string, std::vector<Bit>> TileSegbitsDefault::read_segbits(const std::string &file_path)
    {
        std::map<std::string, std::vector<Bit>> segbits;

        // read file line by line
        std::ifstream in_file(file_path);
        if (!in_file)
        {
            std::cerr << "[ERROR] Database: could not read from file at '" << file_path << "'." << std::endl;
            return {};
        }

        std::string line;
        while (std::getline(in_file, line))
        {
            line = utils::trim(line);
            if (line.empty())
            {
                continue;
            }

            std::vector<Bit> bits;

            // parse the bit positions
            auto parts = utils::split(line, ' ');
            for (auto it = (++parts.begin()); it != parts.end(); it++)
            {
                bits.push_back(parse_bit(*it));
            }

            segbits.emplace(parts.at(0), bits);
        }

        return segbits;
    }

    Bit TileSegbitsDefault::parse_bit(const std::string &bit_str)
    {
        std::string str = bit_str;
        bool is_set = true;

        // is bit set?
        if (bit_str.at(0) == '!')
        {
            is_set = false;
            str = bit_str.substr(1);
        }

        // determine position
        auto pos_str = utils::split(str, '_');

        return Bit(std::stoul(pos_str.at(0)), std::stoul(pos_str.at(1)), is_set);
    }

} // namespace bitstream