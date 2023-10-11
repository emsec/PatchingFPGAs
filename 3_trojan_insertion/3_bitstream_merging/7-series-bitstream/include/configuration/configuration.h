#pragma once

#include "configuration/bitstream.h"

namespace bitstream
{

    /**
     * Class holding the entire configuration of an FPGA in the form of frames each consisting of 101 words (Xilinx 7-Series).
     * Allows for reading from and writing to the configuration.
     */
    class Configuration
    {
    public:
        /**
         * Constructor for a configuration object that stores the entire FPGA configuration in the form of frames extracted from the bitstream.
         * 
         * @param[in] frame_map - A map from frame address to a vector of words belonging to the frame.
         * @param[in] address_map - A map from the byte adress of a frame within the entire bitstream to the actual frame address.
         */
        Configuration(std::shared_ptr<Bitstream> bitstream, const std::map<u32, std::vector<u32>> &frame_map, const std::map<u32, u32> &address_map, const bool m_is_compressed = false);

        /**
         * Extracts a configuration object from a bitstream object.
         * 
         * @param[in] part - A part object containing details of the underlying architecture.
         * @param[in] b_stream - A bitstream object containing the entire bitstream.
         * @returns A pointer to the configuration object.
         */
        static std::shared_ptr<Configuration> from_bitstream(std::shared_ptr<const Part> part, std::shared_ptr<Bitstream> bitstream);

        /**
         * Converts a configuration object into a bitstream object.
         * 
         * @returns A pointer to the bitstream object.
         */
        std::shared_ptr<Bitstream> to_bitstream();

        /**
         * Get all frames of the comnfiguration.
         * 
         * @returns A map of frame address to a vector containing the frame's words.
         */
        const std::map<u32, std::vector<u32>> &get_frames() const { return m_frame_address_to_frame; }

        /**
         * Get the frame at the specified frame address.
         * 
         * @param[in] frame_address - Frame address of the frame to retrieve.
         * @returns A vector of words belonging to the frame specified by the frame address.
         */
        const std::vector<u32> &get_frame(u32 frame_address) const { return m_frame_address_to_frame.at(frame_address); };

        /**
         * Translate a bitstream byte address into a frame address.
         * 
         * @param[in] byte_address - The address of a byte within a frame.
         * @returns The frame address of the frame containing the specified byte.
         */
        u32 get_frame_address(u32 byte_address) const;

        /**
         * Translate a frame address into a bitstream byte address.
         * 
         * @param[in] frame_address - The address of the frame.
         * @returns The byte address of the first byte belonging to the specified frame.
         */
        u32 get_byte_address(u32 frame_address) const { return m_frame_to_byte_address.at(frame_address); }

        /**
         * Get all set configuration bits, i.e., bits that are equal to 1.
         * Returns two sets for each frame that contains a bit that is set to 1:
         *  - A set of words containing such bits.
         *  - A set of bit indexes addressing each bit within the frame.
         * 
         * @returns A map from a frame address to the bits bthat are set within that frame.
         */
        std::map<u32, std::pair<std::set<u32>, std::set<u32>>> get_set_bits() const;

        /**
         * Set (or clear) the bit at the specified location.
         * 
         * @param[in] frame_address - The address of the frame holding the bit.
         * @param[in] word_address - The address of the word holding the bit within the frame.
         * @param[in] bit_index - The index of the bit within the specified word.
         * @param[in] set - True to set the bit, false to clear it.
         * @returns True on success, false otherwise.
         */
        bool set_bit(u32 frame_address, u32 word_address, u32 bit_index, bool set = true);

        /**
         * Update the error correction codes for all updated frames.
         * 
         * @returns True on success, false otherwise.
         */
        bool update_ecc();

        /**
         * Print the content of the frame with the specified content to the console.
         */
        void print_frame(const u32 frame_address, const std::vector<u32> word_offsets = {}) const;

    private:
        // uses bitstream compression?
        bool m_is_compressed = false;

        // pointer to a bitstream object
        std::shared_ptr<Bitstream> m_bitstream;

        // mapping frames addresses to frame data
        std::map<u32, std::vector<u32>> m_frame_address_to_frame;

        // mapping bitstream byte addresses to frame addresses
        std::map<u32, u32> m_byte_to_frame_address;

        // mapping frame addresses to bitstream byte addresses
        std::map<u32, u32> m_frame_to_byte_address;

        // words within frames that have been updated since reading the configuration from the bitstream
        std::map<u32, std::set<u32>> m_updated_words;
    };

} // namespace bitstream
