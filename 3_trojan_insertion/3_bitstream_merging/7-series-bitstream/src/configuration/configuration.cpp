#include "configuration/configuration.h"

#include <iomanip>
#include <iostream>

namespace bitstream
{

    Configuration::Configuration(std::shared_ptr<Bitstream> bitstream, const std::map<u32, std::vector<u32>> &frame_map, const std::map<u32, u32> &address_map, const bool is_compressed) : m_bitstream(bitstream), m_frame_address_to_frame(std::move(frame_map)), m_byte_to_frame_address(std::move(address_map)), m_is_compressed(is_compressed)
    {
        for (const auto &[byte_addr, frame_addr] : m_byte_to_frame_address)
        {
            m_frame_to_byte_address[frame_addr] = byte_addr;
        }
    }

    std::shared_ptr<Configuration> Configuration::from_bitstream(std::shared_ptr<const Part> part, std::shared_ptr<Bitstream> bitstream)
    {
        // registers
        u32 cmd_reg = 0;
        u32 far_reg = 0;
        u32 mask_reg = 0;
        u32 ctl1_reg = 0;

        // Internal state machine for writes.
        bool start_new_write = false;
        bool start_compressed_write = false;
        bool is_compressed = false;
        FrameAddress current_frame_address = 0;
        FrameAddress base_frame_address = 0;

        std::map<u32, std::vector<u32>> frame_map;
        std::map<u32, u32> address_map;

        for (const auto &packet : bitstream->get_packets())
        {
            // skip non-write packets
            if (packet.opcode() != ConfigurationPacket::Opcode::Write)
            {
                continue;
            }

            const auto &data = packet.data();
            auto start_packet_address = packet.bitstream_address() + 4;

            switch (packet.address())
            {
            case ConfigurationRegister::MASK:
                if (data.size() < 1)
                {
                    continue;
                }

                mask_reg = data[0];
                break;

            case ConfigurationRegister::CTL1:
                if (data.size() < 1)
                {
                    continue;
                }

                // enable bitstream compression
                if (((data[0] >> 12) & 0x1) == 0x1)
                {
                    is_compressed = true;
                }

                ctl1_reg |= data[0] & mask_reg;
                break;

            case ConfigurationRegister::CMD:
                if (data.size() < 1)
                {
                    continue;
                }

                cmd_reg = data[0];
                if (cmd_reg == 0x1) // WCFG
                {
                    start_new_write = true;
                }
                else if (cmd_reg == 0x2) // MFW
                {
                    start_compressed_write = true;
                }
                break;

            case ConfigurationRegister::IDCODE:
                if (data.size() < 1)
                {
                    continue;
                }

                if (data[0] != part->idcode())
                {
                    std::cerr << "[ERROR] Configuration: id-code of bitstream '" << std::hex << std::uppercase << std::setw(8) << std::setfill('0') << data[0] << "' does not match id-code of part file '" << std::setw(8) << part->idcode() << "'." << std::endl;
                    return {};
                }
                break;

            case ConfigurationRegister::FAR:
                if (data.size() < 1)
                {
                    continue;
                }

                far_reg = data[0];

                if (((ctl1_reg >> 21) & 0x1) == 0 && cmd_reg == 0x1)
                {
                    start_new_write = true;
                }
                break;

            case ConfigurationRegister::FDRI:
                if (start_new_write)
                {
                    current_frame_address = far_reg;
                    start_new_write = false;
                }

                // frame size of 101 words
                for (unsigned int i = 0; i < data.size(); i += 101)
                {
                    // when compression is turned on, Vivado appears to be overwriting some frames (bug?)
                    if (frame_map.find(u32(current_frame_address)) == frame_map.end())
                    {
                        frame_map[u32(current_frame_address)] = std::vector<u32>(data.begin() + i, data.begin() + i + 101);
                        address_map[start_packet_address + (i * 4)] = u32(current_frame_address);
                    }

                    // used for compressed bitstreams: the last frame may be written to additional addresses using the MFWR register
                    base_frame_address = current_frame_address;

                    auto next_address = part->get_next_frame_address(current_frame_address);
                    if (!next_address)
                    {
                        break;
                    }

                    // there appears to be two frames of padding between rows
                    if (next_address && (next_address->block_type() != current_frame_address.block_type() || next_address->is_bottom_half() != current_frame_address.is_bottom_half() || next_address->row() != current_frame_address.row()))
                    {
                        i += 202;
                    }

                    current_frame_address = *next_address;
                }

                break;

            case ConfigurationRegister::MFWR:
                // skip first write, since it has already been done when calling FDRI
                if (start_compressed_write)
                {
                    start_compressed_write = false;
                    break;
                }

                // write same frame as before
                current_frame_address = far_reg;
                frame_map[u32(current_frame_address)] = frame_map.at(u32(base_frame_address));
                address_map[start_packet_address] = u32(current_frame_address);

                break;

            default:
                break;
            }
        }

        std::cout << "[INFO] Configuration: successfully parsed " << std::dec << frame_map.size() << " frames." << std::endl;

        return std::make_shared<Configuration>(bitstream, frame_map, address_map, is_compressed);
    }

    std::shared_ptr<Bitstream> Configuration::to_bitstream()
    {
        if (m_is_compressed)
        {
            std::cout << "[ERROR] Configuration: this is not yet supported for compressed bitstreams." << std::endl;
            return nullptr;
        }

        update_ecc();

        for (const auto &[frame_address, word_addresses] : m_updated_words)
        {
            const auto frame_it = m_frame_address_to_frame.find(frame_address);
            if (frame_it == m_frame_address_to_frame.end())
            {
                std::cout << "[INFO] Configuration: could not convert configuration to bitstream." << std::endl;
                return nullptr;
            }
            auto &frame = frame_it->second;

            auto byte_address = m_frame_to_byte_address.at(frame_address);

            for (auto word_address : word_addresses)
            {
                auto word = frame.at(word_address);

                // word = byte[i] || byte[i+1] || byte[i+2] || byte [i+3]
                if (!m_bitstream->update_word(byte_address + 4 * word_address, word))
                {
                    // error printed in subfunction
                    return nullptr;
                }
            }
        }

        m_bitstream->update_crc();

        m_updated_words.clear();

        return m_bitstream;
    }

    u32 Configuration::get_frame_address(u32 byte_address) const
    {
        return (--m_byte_to_frame_address.upper_bound(byte_address))->second;
    }

    std::map<u32, std::pair<std::set<u32>, std::set<u32>>> Configuration::get_set_bits() const
    {
        std::map<u32, std::pair<std::set<u32>, std::set<u32>>> res;
        std::vector<u32> zero_frame(101);

        bool first = true;

        for (const auto &[frame_address, words] : m_frame_address_to_frame)
        {
            // skip empty frames
            if (words == zero_frame)
            {
                continue;
            }

            // iterate words
            for (u32 i = 0; i < words.size(); i++)
            {
                // iterate bits
                for (u32 j = 0; j < 32; j++)
                {
                    // ignore frame checksum
                    if (i != 50 || j > 12)
                    {
                        // check if bit is set
                        if ((words.at(i) & (1 << j)) != 0)
                        {
                            res[frame_address].first.insert(i);
                            res[frame_address].second.insert(i * 32 + j);
                        }
                    }
                }
            }
        }

        return res;
    }

    bool Configuration::set_bit(u32 frame_address, u32 word_address, u32 bit_index, bool set)
    {
        if (m_is_compressed)
        {
            std::cout << "[ERROR] Configuration: this is not yet supported for compressed bitstreams." << std::endl;
            return false;
        }

        // valid frame address?
        const auto frame_it = m_frame_address_to_frame.find(frame_address);
        if (frame_it == m_frame_address_to_frame.end())
        {
            std::cout << "[INFO] Configuration: could not set bit in frame with address 0x" << std::setw(8) << std::setfill('0') << std::hex << frame_address << "." << std::endl;
            return false;
        }
        auto &frame = frame_it->second;

        // valid frame size?
        if (word_address >= frame.size())
        {
            std::cout << "[INFO] Configuration: could not set bit in frame with address 0x" << std::setw(8) << std::setfill('0') << std::hex << frame_address << "." << std::endl;
            return false;
        }

        if (set)
        {
            // set bit to 1
            frame.at(word_address) |= 0x1 << bit_index;
        }
        else
        {
            // set bit to 0
            frame.at(word_address) &= 0xFFFFFFFF ^ (0x1 << bit_index);
        }

        m_updated_words[frame_address].insert(word_address);

        return true;
    }

    bool Configuration::update_ecc()
    {
        if (m_is_compressed)
        {
            std::cout << "[ERROR] Configuration: this is not yet supported for compressed bitstreams." << std::endl;
            return false;
        }

        for (const auto &updated_frame : m_updated_words)
        {
            auto frame_address = updated_frame.first;
            const auto frame_it = m_frame_address_to_frame.find(frame_address);
            if (frame_it == m_frame_address_to_frame.end())
            {
                std::cout << "[INFO] Configuration: could not update ECC in frame with address 0x" << std::setw(8) << std::setfill('0') << std::hex << frame_address << "." << std::endl;
                return false;
            }
            auto &frame = frame_it->second;

            u32 ecc = 0;
            u32 data_word;

            for (u32 i = 0; i < 101; i++)
            {
                data_word = frame.at(i);

                // compute bit offset
                u32 val = i * 32;

                // avoid 0x800 (TODO: that's not what's happening here)
                if (i > 0x25)
                {
                    val += 0x1360;
                }
                // avoid 0x400 (TODO: that's not what's happening here)
                else if (i > 0x6)
                {
                    val += 0x1340;
                }
                // avoid lower
                else
                {
                    val += 0x1320;
                }

                // ignore current ECC value of frame
                if (i == 50)
                {
                    data_word &= 0xFFFFE000;
                }

                // compute new ECC
                for (int j = 0; j < 32; j++)
                {
                    if (data_word & 1)
                    {
                        ecc ^= val + j;
                    }

                    data_word >>= 1;
                }
            }

            // compute parity bit for new ECC value
            u32 v = ecc & 0xFFF;
            v ^= v >> 8;
            v ^= v >> 4;
            v ^= v >> 2;
            v ^= v >> 1;
            ecc ^= (v & 1) << 12;

            // Replace the old ECC with the new.
            frame.at(50) &= 0xFFFFE000;
            frame.at(50) |= (ecc & 0x1FFF);

            m_updated_words[frame_address].insert(50);
        }
        return true;
    }

    void Configuration::print_frame(const u32 frame_address, const std::vector<u32> word_offsets) const
    {
        if (const auto it = m_frame_address_to_frame.find(frame_address); it != m_frame_address_to_frame.end())
        {
            const auto frame = it->second;

            std::cout << "0x" << std::setw(8) << std::setfill('0') << std::hex << frame_address << ": ";

            if (word_offsets.empty())
            {
                for (const auto word : frame)
                {
                    std::cout << std::setw(8) << std::setfill('0') << std::hex << word;
                }
            }
            else
            {
                for (const auto offset : word_offsets)
                {
                    if (offset >= 101)
                    {
                        std::cout << std::endl
                                  << "[ERROR] Configuration: Invalid word offset" << std::dec << offset << ".";
                        return;
                    }

                    std::cout << std::setw(8) << std::setfill('0') << std::hex << frame.at(offset);
                }
            }

            std::cout << std::endl;
        }
        else
        {
            std::cout << "[ERROR] Configuration: Invalid frame address 0x" << std::setw(8) << std::setfill('0') << std::hex << frame_address << ".";
        }
    }

} // namespace bitstream