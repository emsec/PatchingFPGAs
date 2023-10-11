#pragma once

#include "architecture/block_type.h"
#include "defines.h"

#include <yaml-cpp/yaml.h>

#include <cstdint>
#include <ostream>

#ifdef _GNU_SOURCE
#undef minor
#endif

namespace bitstream
{

    // TODO documentation
    class FrameAddress
    {
    public:
        FrameAddress() { m_address.addr = 0; }

        FrameAddress(u32 address) { m_address.addr = address; };

        FrameAddress(BlockType block_type, bool is_bottom_half, u8 row, u16 column, u8 minor);

        operator u32() const { return m_address.addr; }

        BlockType block_type() const;
        bool is_bottom_half() const;
        u32 row() const;
        u32 column() const;
        u32 minor() const;

    private:
        union {
            struct
            {
                u32 minor : 7;
                u32 column : 10;
                u32 row : 5;
                u32 is_bottom_half : 1;
                u32 block_type : 3;
                u32 reserved : 6;
            } addr_bits;
            u32 addr;
        } m_address;
    };

    std::ostream &operator<<(std::ostream &o, const FrameAddress &addr);

} // namespace bitstream

namespace YAML
{

    template <>
    struct convert<bitstream::FrameAddress>
    {
        static Node encode(const bitstream::FrameAddress &rhs);
        static bool decode(const Node &node, bitstream::FrameAddress &lhs);
    };

} // namespace YAML
