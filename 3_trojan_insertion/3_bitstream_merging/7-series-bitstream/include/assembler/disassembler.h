#pragma once

#include "assembler/fasm.h"
#include "configuration/configuration.h"
#include "database/database.h"
#include "database/grid.h"

namespace bitstream
{

    /**
     * FASM disassembler to convert bitstream information into FASM lines.
     */
    class Disassembler
    {
    public:
        /**
         * Constructor for a Disassembler object.
         *
         * @param[in] db - Database instance holding the tile type to segbits mapping.
         */
        Disassembler(std::shared_ptr<Database> db);

        /**
         * Translate the configuration of the device into FASM features and add them to an existing FASM file.
         * 
         * @returns A textual description of the features.
         */
        bool add_configuration_to_features(std::shared_ptr<Configuration> config, std::shared_ptr<FASM> fasm_file);

    private:
        std::shared_ptr<const Grid> m_grid;
        std::shared_ptr<Database> m_db;
    };

} // namespace bitstream