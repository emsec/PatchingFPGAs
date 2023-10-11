#pragma once

#include "database/grid.h"
#include "database/tile_data.h"
#include "utils/utils.h"

#include <fstream>
#include <map>
#include <set>

namespace bitstream
{

    // TODO documentation
    class TileSegbits
    {
    public:
        enum class PseudoPIPType
        {
            ALWAYS,
            DEFAULT,
            HINT
        };

        TileSegbits() {}

        // bit_data is map from frame_address to set(bit_index within frame)
        virtual std::map<std::string, std::vector<std::pair<u32, u32>>> bits_to_features(BlockType block_type, const Bits &bits, const std::map<u32, std::pair<std::set<u32>, std::set<u32>>> &bit_data) = 0;

        virtual std::map<BlockType, std::vector<std::pair<Bit, bool>>> features_to_bits(const std::map<BlockType, Bits> &bits, const std::map<std::string, bool> &features) = 0;

    protected:
        std::map<std::string, PseudoPIPType> m_ppips;

        std::map<std::string, TileSegbits::PseudoPIPType> read_ppips(const std::string &file_path)
        {
            std::map<std::string, PseudoPIPType> ppips;

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

                // parse the bit positions
                auto parts = utils::split(line, ' ');
                if (parts.size() != 2)
                {
                    continue;
                }

                PseudoPIPType pip_type;

                if (parts.at(1) == "always")
                {
                    ppips.emplace(parts.at(0), PseudoPIPType::ALWAYS);
                }
                else if (parts.at(1) == "default")
                {
                    ppips.emplace(parts.at(0), PseudoPIPType::DEFAULT);
                }
                else if (parts.at(1) == "hint")
                {
                    ppips.emplace(parts.at(0), PseudoPIPType::HINT);
                }
            }

            return ppips;
        }
    };

} // namespace bitstream