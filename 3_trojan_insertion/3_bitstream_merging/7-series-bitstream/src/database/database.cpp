#include "database/database.h"
#include "database/tile_data.h"
#include "database/tile_segbits_alias.h"
#include "database/tile_segbits_default.h"
#include "utils/memory_mapped_file.h"
#include "utils/utils.h"

#include <rapidjson/document.h>
#include <rapidjson/istreamwrapper.h>

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iostream>

namespace bitstream
{
    Database::Database(const std::string &db_root, Part part) : m_db_root(db_root), m_part(part)
    {
        const std::string comp_begin = "tile_type_";
        const std::string comp_end = ".json";

        for (const auto &entry : std::filesystem::directory_iterator(m_db_root))
        {
            const std::string filename = entry.path().filename().string();
            if (utils::begins_with(filename, comp_begin) && utils::ends_with(filename, comp_end))
            {
                std::string tile_type = utils::to_lower(filename.substr(10, filename.size() - comp_begin.size() - comp_end.size()));

                std::string segbits_clb_io_clk_path = m_db_root + "/" + "segbits_" + tile_type + ".db";
                if (!std::filesystem::is_regular_file(segbits_clb_io_clk_path))
                {
                    segbits_clb_io_clk_path = "";
                }

                std::string segbits_bram_path = m_db_root + "/" + "segbits_" + tile_type + ".block_ram.db";
                if (!std::filesystem::is_regular_file(segbits_bram_path))
                {
                    segbits_bram_path = "";
                }

                std::string ppips_path = m_db_root + "/" + "ppips_" + tile_type + ".db";
                if (!std::filesystem::is_regular_file(ppips_path))
                {
                    ppips_path = "";
                }

                std::string mask_path = m_db_root + "/" + "mask_" + tile_type + ".db";
                if (!std::filesystem::is_regular_file(mask_path))
                {
                    mask_path = "";
                }

                std::string tile_type_path = m_db_root + "/" + "tile_type_" + tile_type + ".db";
                if (!std::filesystem::is_regular_file(tile_type_path))
                {
                    tile_type_path = "";
                }

                m_tile_type_to_tile_data.emplace(utils::to_upper(tile_type), TileData(segbits_clb_io_clk_path, segbits_bram_path, ppips_path, mask_path, tile_type_path));
            }
        }
    }

    std::shared_ptr<Database> Database::from_file(const std::string &db_root, Part part)
    {
        std::shared_ptr<Database> database = std::make_shared<Database>(db_root, part);

        if (!database->read_tilegrid())
        {
            return nullptr;
        }

        return database;
    }

    std::shared_ptr<const Grid> Database::get_grid() const
    {
        return m_grid;
    }

    std::shared_ptr<TileSegbits> Database::get_tile_segbits(std::string tile_name)
    {
        auto grid_info = m_grid->get_grid_info(tile_name);
        const auto &tile_type = grid_info->type();
        const auto &bits = grid_info->bits();

        // has alias?
        if (std::any_of(bits.begin(), bits.end(), [](std::pair<BlockType, Bits> bb) { return bb.second.alias().has_value(); }))
        {
            if (const auto &type_it = m_tile_type_to_tile_data.find(tile_type); type_it != m_tile_type_to_tile_data.end())
            {
                std::function<std::shared_ptr<TileSegbits>(std::string)> db_get_tile_segbits = std::bind(&Database::get_tile_segbits_from_type, this, std::placeholders::_1);
                return std::make_shared<TileSegbitsAlias>(type_it->second, tile_type, bits, db_get_tile_segbits);
            }
            else
            {
                std::cerr << "[ERROR] Database: no tile data found for tile type '" << tile_type << "'." << std::endl;
                return nullptr;
            }
        }
        else
        {
            return get_tile_segbits_from_type(tile_type);
        }
    }

    bool Database::read_tilegrid()
    {
        std::string file_path = m_db_root + "/" + m_part.device_family() + "/tilegrid.json";

        std::ifstream in_file(file_path);
        if (!in_file)
        {
            std::cerr << "[ERROR] Database: could not read from file at '" << file_path << "'." << std::endl;
            return false;
        }

        rapidjson::IStreamWrapper in_wrapper(in_file);

        rapidjson::Document tilegrid;
        tilegrid.ParseStream(in_wrapper);

        // actually read tilegrid
        m_grid = std::make_shared<Grid>(tilegrid);

        std::cout << "[INFO] Database: successfully read tilegrid from file '" << file_path << "'." << std::endl;

        return true;
    }

    std::shared_ptr<TileSegbits> Database::get_tile_segbits_from_type(std::string tile_type)
    {
        if (const auto &segbit_it = m_tile_type_to_tile_segbits.find(tile_type); segbit_it != m_tile_type_to_tile_segbits.end())
        {
            return segbit_it->second;
        }
        else if (const auto &type_it = m_tile_type_to_tile_data.find(tile_type); type_it != m_tile_type_to_tile_data.end())
        {
            m_tile_type_to_tile_segbits[tile_type] = std::make_shared<TileSegbitsDefault>(type_it->second);
            return m_tile_type_to_tile_segbits.at(tile_type);
        }
        else
        {
            std::cerr << "[ERROR] Database: no tile data found for tile type '" << tile_type << "'." << std::endl;
            return nullptr;
        }
    }

} // namespace bitstream
