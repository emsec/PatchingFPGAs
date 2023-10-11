#pragma once

#include <ostream>

namespace bitstream
{

    // TODO documentation
    // Series-7 configuration register addresses
    // according to UG470, pg. 109
    enum class ConfigurationRegister : unsigned int
    {
        CRC = 0x00,
        FAR = 0x01,
        FDRI = 0x02,
        FDRO = 0x03,
        CMD = 0x04,
        CTL0 = 0x05,
        MASK = 0x06,
        STAT = 0x07,
        LOUT = 0x08,
        COR0 = 0x09,
        MFWR = 0x0a,
        CBC = 0x0b,
        IDCODE = 0x0c,
        AXSS = 0x0d,
        COR1 = 0x0e,
        WBSTAR = 0x10,
        TIMER = 0x11,
        UNKNOWN = 0x13,
        BOOTSTS = 0x16,
        CTL1 = 0x18,
        BSPI = 0x1F,
    };

    enum class CommandRegisterCode : unsigned int
    {
        NOP = 0x00,
        WCFG = 0x01,
        MFW = 0x02,
        LFRM = 0x03,
        RCFG = 0x04,
        START = 0x05,
        RCAP = 0x06,
        RCRC = 0x07,
        AGHIGH = 0x08,
        SWITCH = 0x09,
        GRESTORE = 0x0A,
        SHUTDOWN = 0x0B,
        GCAPTURE = 0x0C,
        DESYNC = 0x0D,
        RES = 0x0E,
        IPROG = 0x0F,
        CRCC = 0x10,
        LTIMER = 0x11,
        BSPI_READ = 0x12,
        FALL_EDGE = 0x13
    };

    std::ostream &operator<<(std::ostream &o, const ConfigurationRegister &value);
    std::ostream &operator<<(std::ostream &o, const CommandRegisterCode &value);

} // namespace bitstream