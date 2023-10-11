#pragma once

#include "architecture/part.h"
#include "database/grid.h"
#include "database/tile_segbits.h"

#include <map>
#include <string>

namespace bitstream
{

    // TODO documentation
    class Database
    {
    public:
        Database(const std::string &db_root, Part part);
        static std::shared_ptr<Database> from_file(const std::string &db_root, Part part);

        std::shared_ptr<const Grid> get_grid() const;
        std::shared_ptr<TileSegbits> get_tile_segbits(std::string tile_name);

    private:
        std::string m_db_root;
        Part m_part;
        std::shared_ptr<const Grid> m_grid;
        std::map<std::string, TileData> m_tile_type_to_tile_data;
        std::map<std::string, std::shared_ptr<TileSegbits>> m_tile_type_to_tile_segbits;

        bool read_tilegrid();
        std::shared_ptr<TileSegbits> get_tile_segbits_from_type(std::string tile_type);
    };

} // namespace bitstream