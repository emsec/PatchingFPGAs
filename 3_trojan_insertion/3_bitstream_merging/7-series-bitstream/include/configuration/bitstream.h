#pragma once

#include "architecture/frame_address.h"
#include "architecture/part.h"
#include "configuration/configuration_packet.h"
#include "defines.h"

#include <iterator>
#include <optional>
#include <vector>

namespace bitstream
{

    // TODO documentation
    class Bitstream
    {
    public:
        Bitstream(const std::vector<u8> &bytes) : m_bytes(bytes) {}
        static std::shared_ptr<Bitstream> from_file(const std::string &file_path);
        bool to_file(const std::string &file_path) const;
        const std::vector<u8> &get_bytes() const { return m_bytes; }
        const std::vector<u32> &get_words() const { return m_words; };
        const std::vector<ConfigurationPacket> &get_packets() const { return m_packets; }
        u32 get_sync_offset() const { return m_sync_offset; }
        bool initialize();
        bool update_word(u32 start_address, u32 word);
        bool packets_to_file(const std::string &file_path) const;

        /**
         * Update the CRC values of the bitstream.
         * 
         * @returns True on success, false otherwise.
         */
        bool update_crc();

    private:
        std::vector<u8> m_bytes;
        std::vector<u32> m_words;
        std::vector<ConfigurationPacket> m_packets;
        u32 m_sync_offset;

        bool init_words();
        bool init_packets();
    };

} // namespace bitstream