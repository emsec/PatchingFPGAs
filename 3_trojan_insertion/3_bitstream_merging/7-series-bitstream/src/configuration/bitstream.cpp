#include "configuration/bitstream.h"
#include "utils/memory_mapped_file.h"

#include <fstream>
#include <iomanip>
#include <iostream>
#include <vector>

namespace bitstream
{

    std::shared_ptr<Bitstream> Bitstream::from_file(const std::string &file_path)
    {
        auto in_file = bitstream::utils::MemoryMappedFile::init_with_file(file_path);
        if (!in_file)
        {
            std::cerr << "[ERROR] Bitstream: could not read from file at '" << file_path << "'." << std::endl;
            return nullptr;
        }

        std::cout << "[INFO] Bitstream: successfully read " << std::dec << in_file->size() << " bytes from '" << file_path << "'." << std::endl;

        auto b_stream = std::make_shared<Bitstream>(std::vector<u8>(static_cast<u8 *>(in_file->data()), static_cast<u8 *>(in_file->data()) + in_file->size()));

        if (!b_stream->initialize())
        {
            return nullptr;
        }

        return b_stream;
    }

    bool Bitstream::to_file(const std::string &file_path) const
    {
        std::ofstream out_file(file_path);
        if (!out_file)
        {
            std::cerr << "[ERROR] Bitstream: could not write bitstream to file at '" << file_path << "'." << std::endl;
            return false;
        }

        out_file.write((char *)m_bytes.data(), m_bytes.size());

        std::cout << "[INFO] Bitstream: successfully wrote " << std::dec << m_bytes.size() << " bytes to '" << file_path << "'." << std::endl;
        return true;
    }

    bool Bitstream::initialize()
    {
        if (!init_words())
        {
            return false;
        }

        if (!init_packets())
        {
            return false;
        }

        return true;
    }

    bool Bitstream::update_word(u32 start_address, u32 word)
    {
        if (start_address + 4 >= m_bytes.size() || start_address < m_sync_offset)
        {
            std::cerr << "[ERROR] Bitstream: could not update bitstream data." << std::endl;
            return false;
        }

        // update packets
        for (auto packet_it = m_packets.begin(); packet_it != m_packets.end(); packet_it++)
        {
            auto packet_address = packet_it->bitstream_address();

            if (start_address == packet_address)
            {
                std::cerr << "[ERROR] Bitstream: could not set packet data at bitstream address " << std::hex << std::setfill('0') << std::setw(8) << start_address << "." << std::endl;
                return false;
            }

            if (packet_address < start_address && start_address <= (packet_address + packet_it->data().size() * 4))
            {
                if (!packet_it->update_word((start_address - packet_address - 4) / 4, word))
                {
                    std::cerr << "[ERROR] Bitstream: could not set packet data at bitstream address " << std::hex << std::setfill('0') << std::setw(8) << start_address << "." << std::endl;
                    return false;
                }
                break;
            }
        }

        // update words
        m_words[(start_address - m_sync_offset) / 4] = word;

        // update bytes
        m_bytes[start_address] = (u8)((word >> 24) & 0xFF);
        m_bytes[start_address + 1] = (u8)((word >> 16) & 0xFF);
        m_bytes[start_address + 2] = (u8)((word >> 8) & 0xFF);
        m_bytes[start_address + 3] = (u8)(word & 0xFF);

        return true;
    }

    bool Bitstream::packets_to_file(const std::string &file_path) const
    {
        std::ofstream out_file(file_path);
        if (!out_file)
        {
            std::cerr << "[ERROR] Bitstream: could not write packets to file at '" << file_path << "'." << std::endl;
            return false;
        }

        for (const auto &packet : m_packets)
        {
            out_file << packet;
        }

        std::cout << "[INFO] Bitstream: successfully wrote " << std::dec << m_packets.size() << " packets to '" << file_path << "'." << std::endl;
        return true;
    }

    bool Bitstream::init_words()
    {
        const std::vector<u8> sync_word = {0xAA, 0x99, 0x55, 0x66};

        m_words.clear();

        // find sync word
        auto sync_pos = std::search(m_bytes.begin(), m_bytes.end(), sync_word.begin(), sync_word.end());
        if (sync_pos == m_bytes.end())
        {
            std::cerr << "[ERROR] Bitstream: input does not contain a SYNC word." << std::endl;
            return false;
        }
        sync_pos += sync_word.size();

        m_sync_offset = std::distance(m_bytes.begin(), sync_pos);

        std::vector<u8> tmp(sync_pos, m_bytes.end());

        auto len = tmp.size();
        if (len % 4 != 0)
        {
            std::cerr << "[ERROR] Bitstream: byte length of bitstream is not a multiple of 32 bits." << std::endl;
            return false;
        }

        // convert to 32-bit words
        for (auto it = tmp.begin(); it < tmp.end() - 4; it += 4)
        {
            u32 word = ((*it) << 24) ^ ((*(it + 1)) << 16) ^ ((*(it + 2)) << 8) ^ (*(it + 3));
            m_words.push_back(word);
        }

        std::cout << "[INFO] Bitstream: successfully parsed " << std::dec << m_words.size() << " words after SYNC word." << std::endl;

        return true;
    }

    bool Bitstream::init_packets()
    {
        u32 current_byte_address = m_sync_offset;

        m_packets.clear();

        auto words_it = m_words.begin();
        while (words_it != m_words.end())
        {
            auto header_type = static_cast<ConfigurationPacket::Type>(((*words_it) >> 29) & 0x7);

            switch (header_type)
            {
            case ConfigurationPacket::Type::NONE:
            {
                m_packets.push_back(ConfigurationPacket(current_byte_address, header_type, ConfigurationPacket::Opcode::NOP, ConfigurationRegister::CRC, {}));
                current_byte_address += 4;
                words_it += 1;
                break;
            }
            case ConfigurationPacket::Type::TYPE1:
            {
                ConfigurationPacket::Opcode opcode = static_cast<ConfigurationPacket::Opcode>(((*words_it) >> 27) & 0x3);
                ConfigurationRegister address = static_cast<ConfigurationRegister>(((*words_it) >> 13) & 0x3FFF);
                u32 data_word_count = (*words_it) & 0x7FF;

                // Incomplete packet
                if (words_it > m_words.end() - (data_word_count + 1))
                {
                    std::cerr << "[ERROR] Bitstream: invalid TYPE1 packet." << std::endl;
                    return false;
                }

                m_packets.push_back(ConfigurationPacket(current_byte_address, header_type, opcode, address, std::vector<u32>(words_it + 1, words_it + data_word_count + 1)));
                current_byte_address += 4 * data_word_count + 4;
                words_it += data_word_count + 1;
                break;
            }
            case ConfigurationPacket::Type::TYPE2:
            {
                ConfigurationPacket::Opcode opcode = static_cast<ConfigurationPacket::Opcode>(((*words_it) >> 27) & 0x3);
                u32 data_word_count = (*words_it) & 0x7FFFFFF;

                // Incomplete packet
                if (words_it > m_words.end() - (data_word_count + 1))
                {
                    std::cerr << "[ERROR] Bitstream: invalid TYPE2 packet." << std::endl;
                    return false;
                }

                auto previous_packet = m_packets.back();
                if (previous_packet.header_type() != ConfigurationPacket::Type::TYPE1)
                {
                    std::cerr << "[ERROR] Bitstream: no valid TYPE 1 packet in front of TYPE 2 packet." << std::endl;
                    return false;
                }

                m_packets.push_back(ConfigurationPacket(current_byte_address, header_type, opcode, previous_packet.address(), std::vector<u32>(words_it + 1, words_it + data_word_count + 1)));
                current_byte_address += 4 * data_word_count + 4;
                words_it += data_word_count + 1;
                break;
            }
            default:
            {
                std::cerr << "[ERROR] Bitstream: invalid packet header." << std::endl;
                return false;
            }
            }
        }

        std::cout << "[INFO] Bitstream: successfully parsed " << std::dec << m_packets.size() << " configuration packets." << std::endl;
        return true;
    }

    bool Bitstream::update_crc()
    {
        u32 crc_value = 0;
        u32 crc_poly = 0x1EDC6F41;

        for (const auto &packet : m_packets)
        {
            const auto packet_address = packet.address();
            const auto &packet_data = packet.data();

            // reset CRC value
            if (packet_address == ConfigurationRegister::CMD && packet_data.size() == 1 && static_cast<CommandRegisterCode>(packet_data.at(0)) == CommandRegisterCode::RCRC)
            {
                crc_value = 0;
            }
            else
            {
                // write CRC value
                if (packet.opcode() != ConfigurationPacket::Opcode::NOP && packet_address == ConfigurationRegister::CRC)
                {
                    u32 final_value = 0;

                    for (u32 i = 0; i < 32; i++)
                    {
                        final_value |= ((crc_value >> i) & 0x1) << (31 - i);
                    }

                    update_word(packet.bitstream_address() + 4, final_value);
                }

                // update CRC value
                for (const auto word : packet_data)
                {
                    // compute CRC value of 5-bit register address and 32-bit word
                    u64 crc_input = static_cast<u64>(packet_address) << 32 | word;

                    for (u32 i = 0; i < 37; i++)
                    {
                        u64 tmp = ((crc_value >> 31) ^ (crc_input >> i)) & 0x1;

                        crc_value <<= 1;

                        if (tmp != 0)
                        {
                            crc_value ^= crc_poly;
                        }
                    }
                }
            }
        }

        return false;
    }

} // namespace bitstream
