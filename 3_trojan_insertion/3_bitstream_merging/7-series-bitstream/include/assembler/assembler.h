#pragma once

#include "assembler/fasm.h"
#include "configuration/configuration.h"
#include "database/database.h"
#include "database/grid.h"

namespace bitstream
{

    /**
     * FASM assembler to convert FASM lines into bitstream information.
     */
    class Assembler
    {
    public:
        /**
         * Constructor for an Assembler object.
         *
         * @param[in] db - Database instance holding the tile type to segbits mapping.
         */
        Assembler(std::shared_ptr<Database> db);

        /**
         * Translate the features from the FASM file into the configuration of the device and add them to the existing configuration.
         * 
         * @returns True on success, false otherwise.
         */
        bool add_features_to_configuration(std::shared_ptr<Configuration> config, std::shared_ptr<FASM> fasm_file);

    private:
        std::shared_ptr<const Grid> m_grid;
        std::shared_ptr<Database> m_db;
    };

} // namespace bitstream