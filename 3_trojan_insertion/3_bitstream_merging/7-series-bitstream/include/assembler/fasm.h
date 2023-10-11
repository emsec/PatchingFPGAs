#pragma once

#include "defines.h"

#include <map>
#include <string>
#include <vector>

namespace bitstream
{

    /**
     * Class comprising of FASM lines as read from a file or parsed from a bitstream.
     */
    class FASM
    {
    public:
        /**
         * Default constructor.
         */
        FASM() = default;

        /**
         * Convert a tile name and the corresponding tile type's feature into a FASM line.
         * 
         * @param[in] tile_name - Name of the tile.
         * @param[in] feature - Name of the tile type's feature.
         * @returns True on success, false otherwise.
         */
        bool add_fasm_line(const std::string &tile_name, const std::string &feature);

        /**
         * Get a map from tile names to their corresponding features stored in the FASM file.
         * 
         * @returns A map from tile names to features.
         */
        std::map<std::string, std::map<std::string, bool>> get_features() const;

        /**
         * Output FASM lines to a canonicalized FASM file at the specified location.
         * 
         * @param[in] file_path - Path to the output file.
         * @returns True on success, false otherwise.
         */
        bool to_file(const std::string &file_path) const;

        /**
         * Read FASM lines from the canonicalized FASM file at the specified location.
         * 
         * @param[in] file_path - Path to the input file.
         * @param[in] overwrite - True to overwrite already existing lines, false to keep them.
         * @returns True on success, false otherwise.
         */
        bool from_file(const std::string &file_path, bool overwrite = true);

        /**
         * Print all FASM lines in canonicalized form to std::cout.
         */
        void print() const;

        /**
         * Get the current number of FASM lines.
         * 
         * @returns Number of FASM lines.
         */
        u32 size() const;

    private:
        struct FASMLine
        {
        public:
            std::string tile_name;
            std::string feature;
            std::vector<u32> value_range;
            std::vector<u32> address_range;
        };

        struct SpecialCase
        {
        public:
            std::string search_string;
            u32 offset;
            u32 length;
            u32 bitlength;
        };

        std::map<std::string, FASMLine> m_fasm_lines;
        std::vector<SpecialCase> m_special_cases = {
            {"LUT.INIT", 8, 8, 64},
            {"RAMB18_Y1.INIT_", 17, 15, 256},
            {"ZINIT_", 7, 6, 18},
            {"ZSRVAL_", 8, 7, 18},
            {"ZALMOST_EMPTY_OFFSET", 20, 20, 13},
            {"ZALMOST_FULL_OFFSET", 19, 19, 13},
            {"DSP_0.MASK", 10, 10, 48},
            {"DSP_0.PATTERN", 10, 10, 48},
            {"DSP_1.MASK", 10, 10, 48},
            {"DSP_1.PATTERN", 10, 10, 48}};

        void to_ostream(std::ostream &stream) const;
    };

} // namespace bitstream