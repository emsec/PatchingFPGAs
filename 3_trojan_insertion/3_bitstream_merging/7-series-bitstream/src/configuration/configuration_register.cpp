#include "configuration/configuration_register.h"

namespace bitstream
{

    std::ostream &operator<<(std::ostream &o, const ConfigurationRegister &value)
    {
        switch (value)
        {
        case ConfigurationRegister::CRC:
            return o << "CRC";
        case ConfigurationRegister::FAR:
            return o << "FAR";
        case ConfigurationRegister::FDRI:
            return o << "FDRI";
        case ConfigurationRegister::FDRO:
            return o << "FDRO";
        case ConfigurationRegister::CMD:
            return o << "CMD";
        case ConfigurationRegister::CTL0:
            return o << "CTL0";
        case ConfigurationRegister::MASK:
            return o << "MASK";
        case ConfigurationRegister::STAT:
            return o << "STAT";
        case ConfigurationRegister::LOUT:
            return o << "LOUT";
        case ConfigurationRegister::COR0:
            return o << "COR0";
        case ConfigurationRegister::MFWR:
            return o << "MFWR";
        case ConfigurationRegister::CBC:
            return o << "CBC";
        case ConfigurationRegister::IDCODE:
            return o << "IDCODE";
        case ConfigurationRegister::AXSS:
            return o << "AXSS";
        case ConfigurationRegister::COR1:
            return o << "COR1";
        case ConfigurationRegister::WBSTAR:
            return o << "WBSTAR";
        case ConfigurationRegister::TIMER:
            return o << "TIMER";
        case ConfigurationRegister::BOOTSTS:
            return o << "BOOTSTS";
        case ConfigurationRegister::CTL1:
            return o << "CTL1";
        case ConfigurationRegister::BSPI:
            return o << "BSPI";
        default:
            return o << "Unknown";
        }
    }

    std::ostream &operator<<(std::ostream &o, const CommandRegisterCode &value)
    {
        switch (value)
        {
        case CommandRegisterCode::NOP:
            return o << "NULL";
        case CommandRegisterCode::WCFG:
            return o << "WCFG";
        case CommandRegisterCode::MFW:
            return o << "MFW";
        case CommandRegisterCode::LFRM:
            return o << "LFRM";
        case CommandRegisterCode::RCFG:
            return o << "RCFG";
        case CommandRegisterCode::START:
            return o << "START";
        case CommandRegisterCode::RCAP:
            return o << "RCAP";
        case CommandRegisterCode::RCRC:
            return o << "RCRC";
        case CommandRegisterCode::AGHIGH:
            return o << "AGHIGH";
        case CommandRegisterCode::SWITCH:
            return o << "SWITCH";
        case CommandRegisterCode::GRESTORE:
            return o << "GRESTORE";
        case CommandRegisterCode::SHUTDOWN:
            return o << "SHUTDOWN";
        case CommandRegisterCode::GCAPTURE:
            return o << "GCAPTURE";
        case CommandRegisterCode::DESYNC:
            return o << "DESYNC";
        case CommandRegisterCode::RES:
            return o << "Reserved";
        case CommandRegisterCode::IPROG:
            return o << "IPROG";
        case CommandRegisterCode::CRCC:
            return o << "CRCC";
        case CommandRegisterCode::LTIMER:
            return o << "LTIMER";
        case CommandRegisterCode::BSPI_READ:
            return o << "BSPI_READ";
        case CommandRegisterCode::FALL_EDGE:
            return o << "FALL_EDGE";
        default:
            return o << "Unknown";
        }
    }

} // namespace bitstream
