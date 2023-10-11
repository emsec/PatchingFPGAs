#pragma once

#include "defines.h"

#include <string>

namespace bitstream
{

    /**
     * Struct holding the paths to specific database files containing informations regarding the bits of a single tile type.
     * 
     * The segbits files store information about the bits corresponding to the configuration of a specific tile type.
     */
    struct TileData
    {
    public:
        /**
         * Constructor for a TileData object.
         *
         * @param[in] segbits_clb_io_clk - Path to the file containing bit information of block type CLB_IO_CLK of a single tile type.
         * @param[in] segbits_bram - Path to the file containing bit information of block type BLOCK_RAM of a single tile type.
         * @param[in] ppips - Path to the file containing information about pseudo PIP features.
         * @param[in] mask - Path to the file containing bit masks.
         * @param[in] tile_type - Path to the file containing detailed information on the tile type.
         */
        TileData(const std::string &segbits_clb_io_clk, const std::string &segbits_bram, const std::string &ppips, const std::string &mask, const std::string &tile_type) : m_segbits_clb_io_clk(segbits_clb_io_clk), m_segbits_bram(segbits_bram), m_ppips(ppips), m_mask(mask), m_tile_type(tile_type) {}

        /**
         * Returns the file path of the database file containing bit information of block type CLB_IO_CLK of a single tile type.
         * 
         * @returns The file path.
         */
        const std::string &segbits_clb_io_clk() const { return m_segbits_clb_io_clk; }

        /**
         * Returns the file path of the database file containing bit information of block type BLOCK_RAM of a single tile type.
         * 
         * @returns The file path.
         */
        const std::string &segbits_bram() const { return m_segbits_bram; }

        /**
         * Returns the file path of the database file containing information about pseudo PIP features.
         * 
         * @returns The file path.
         */
        const std::string &ppips() const { return m_ppips; }

        /**
         * Returns the file path of the database file containing bit masks.
         * 
         * @returns The file path.
         */
        const std::string &mask() const { return m_mask; }

        /**
         * Returns the file path of the database file containing detailed information on the tile type.
         * 
         * @returns The file path.
         */
        const std::string &tile_type() const { return m_tile_type; }

    private:
        const std::string m_segbits_clb_io_clk;
        const std::string m_segbits_bram;
        const std::string m_ppips;
        const std::string m_mask;
        const std::string m_tile_type;
    };

    /**
     * Struct holding the position of a bit within the subset of words designated for a given tile type.
     * 
     * The configuration of each tile is specified by a fixed subset of words within the bitstream. These words 
     * are split into columns with their bits forming the respective rows. The 'tilegrid.json' file specifies
     * the base address, offset, and size of these subsets.
     */
    struct Bit
    {
    public:
        /**
         * Constructor for a Bit object.
         *
         * @param[in] word_column - Addresses the word column within the subset of words.
         * @param[in] word_bit - Addresses the bit within the specified column.
         * @param[in] is_set - Specifies whether the bit is set.
         */
        Bit(u32 word_column, u32 word_bit, bool is_set) : m_word_column(word_column), m_word_bit(word_bit), m_is_set(is_set) {}

        /**
         * Returns the word column that the bits is in.
         * 
         * @returns The word column.
         */
        u32 word_column() const { return m_word_column; }

        /**
         * Returns the bit position of the bit within the word column.
         * 
         * @returns The bit position within the column.
         */
        u32 word_bit() const { return m_word_bit; }

        /**
         * Returns whether the bit is set or not.
         * 
         * @returns True if set, false otherwise.
         */
        bool is_set() const { return m_is_set; }

    private:
        u32 m_word_column;
        u32 m_word_bit;
        bool m_is_set;
    };

} // namespace bitstream