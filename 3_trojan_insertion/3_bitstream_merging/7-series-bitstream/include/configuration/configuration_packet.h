#pragma once

#include "configuration/configuration_register.h"
#include "defines.h"

#include <optional>
#include <ostream>
#include <vector>

namespace bitstream
{

    /**
     * Xilinx 7-series configuration packet as specified in UG470 (p. 108)
     */
    class ConfigurationPacket
    {
    public:
        /**
         * Configuration packet header types.
         */
        enum class Type
        {
            NONE = 0,
            TYPE1 = 1,
            TYPE2 = 2
        };

        /**
         * Configuration packet opcodes.
         */
        enum class Opcode
        {
            NOP = 0,
            Read = 1,
            Write = 2,
            Reserved = 3
        };

        /**
         * Create a configuration packet from the data extracted from the bitstream.
         * 
         * @param[in] bitstream_address - The bitstream address.
         * @param[in] header_type - The type of the header.
         * @param[in] opcode - The opcode of the header.
         * @param[in] address - The address of the source or destination register.
         * @param[in] data - The data of the packet.
         */
        ConfigurationPacket(u32 bitstream_address, Type header_type, Opcode opcode, ConfigurationRegister address, const std::vector<u32> &data) : m_bitstream_address(bitstream_address), m_header_type(header_type), m_opcode(opcode), m_address(address), m_data(std::move(data)) {}

        /**
         * Get the starting address of the packet in number of bytes.
         * 
         * @returns The bitstream address.
         */
        u32 bitstream_address() const { return m_bitstream_address; }

        /**
         * Get the type of the configuration packet header.
         * 
         * @returns The type of the header.
         */
        const Type header_type() const { return m_header_type; }

        /**
         * Get the opcode of the configuration packet header.
         * 
         * @returns The opcode of the header.
         */
        const Opcode opcode() const { return m_opcode; }

        /**
         * Get the address of the register specified in the configuration packet header.
         * 
         * @returns The address of the source or destination register.
         */
        const ConfigurationRegister address() const { return m_address; }

        /**
         * Get the data of the configuration packet as a vector of 32-bit words.
         * 
         * @returns The data of the packet.
         */
        const std::vector<u32> &data() const { return m_data; }

        bool update_word(u32 index, u32 word);

    private:
        u32 m_bitstream_address;
        Type m_header_type;
        Opcode m_opcode;
        ConfigurationRegister m_address;
        std::vector<u32> m_data;
    };

    std::ostream &operator<<(std::ostream &o, const ConfigurationPacket &packet);

} // namespace bitstream