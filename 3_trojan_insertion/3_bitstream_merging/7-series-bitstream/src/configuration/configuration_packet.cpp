#include "configuration/configuration_packet.h"

#include <iomanip>
#include <iostream>
#include <ostream>
#include <vector>

namespace bitstream
{

    bool ConfigurationPacket::update_word(u32 index, u32 word)
    {
        if (index >= m_data.size())
        {
            return false;
        }

        m_data[index] = word;

        return true;
    }

    std::ostream &operator<<(std::ostream &o, const ConfigurationPacket &packet)
    {
        if (packet.header_type() == ConfigurationPacket::Type::NONE || packet.opcode() == ConfigurationPacket::Opcode::NOP)
        {
            return o;
        }

        o << std::setw(8) << std::setfill('0') << std::uppercase << std::hex << packet.bitstream_address() << " :: ";

        switch (packet.header_type())
        {
        case ConfigurationPacket::Type::NONE:
            return o << "[Hdr =   NONE] " << std::endl;

        case ConfigurationPacket::Type::TYPE1:
            o << "[Hdr =   TYPE1] ";
            break;

        case ConfigurationPacket::Type::TYPE2:
            o << "[Hdr =   TYPE2] ";
            break;

        default:
            return o << "[Hdr = Invalid] " << std::endl;
        }

        switch (packet.opcode())
        {
        case ConfigurationPacket::Opcode::NOP:
            return o << "[Op =      NOP] " << std::endl;

        case ConfigurationPacket::Opcode::Read:
            o << "[Op =     READ] ";
            break;

        case ConfigurationPacket::Opcode::Write:
            o << "[Op =    WRITE] ";
            break;

        default:
            return o << "[Op = Reserved] " << std::endl;
        }

        o << "[Reg = " << std::setfill(' ') << std::setw(7) << packet.address() << "] ";
        o << "[Cnt = " << std::dec << std::setw(8) << packet.data().size() << "] ";

        if (packet.data().size() == 1)
        {
            auto data = packet.data().at(0);

            switch (packet.address())
            {
            case ConfigurationRegister::CMD:
                o << "[Code  = " << std::setfill(' ') << std::setw(9) << static_cast<CommandRegisterCode>(data) << "] ";
                break;
            default:
                o << "[Value =  " << std::hex << std::setw(8) << std::setfill('0') << data << "] ";
                break;
            }
        }
        else if ((packet.data().size() > 0) && (packet.data().size() <= 10))
        {
            auto data = packet.data();

            o << "[";
            for (auto b : data)
            {
                o << std::hex << std::setw(8) << std::setfill('0') << b;
            }
            o << "]";
        }

        return o << std::endl;
    }

} // namespace bitstream
