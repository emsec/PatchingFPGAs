#include "assembler/fasm.h"
#include "defines.h"
#include "utils/utils.h"

#include <fstream>
#include <iomanip>
#include <iostream>
#include <regex>
#include <sstream>

namespace bitstream {

bool FASM::add_fasm_line(const std::string& tile_name, const std::string& feature)
{
    static std::regex re("([A-Za-z0-9_]+).([^\\[]+)(\\[[0-9]+\\])?");
    std::smatch parts;
    if (!std::regex_match(feature, parts, re)) {
        std::cerr << "[ERROR] FASM: could not match regular expression to feature '" << feature << "' of tile '" << tile_name << "'." << std::endl;
        return false;
    }

    std::string fasm_feature = parts[2].str();

    if (const auto it = m_fasm_lines.find(tile_name + "." + fasm_feature); it == m_fasm_lines.end()) {
        FASMLine fasm_line;

        fasm_line.tile_name = tile_name;
        fasm_line.feature = fasm_feature;
        fasm_line.value_range.push_back(1);

        if (parts[3].length() > 0) {
            std::string addr_str = parts[3].str();
            try {
                fasm_line.address_range.push_back(std::stoul(addr_str.substr(1, addr_str.size() - 2)));
            } catch (...) {
                std::cerr << "[ERROR] FASM: could not read address of feature '" << fasm_line.feature << "' for tile '" << fasm_line.tile_name << "'." << std::endl;
                return false;
            }
        }

        m_fasm_lines.emplace(fasm_line.tile_name + "." + fasm_line.feature, fasm_line);
    } else {
        std::string addr_str = parts[3].str();
        try {
            it->second.address_range.push_back(std::stoul(addr_str.substr(1, addr_str.size() - 2)));
        } catch (...) {
            std::cerr << "[ERROR] FASM: could not read address of feature '" << it->second.feature << "' for tile '" << it->second.tile_name << "'." << std::endl;
            return false;
        }

        it->second.value_range.push_back(1);
    }

    return true;
}

std::map<std::string, std::map<std::string, bool>> FASM::get_features() const
{
    std::map<std::string, std::map<std::string, bool>> tile_names_to_features;

    for (const auto& [target, fasm_line] : m_fasm_lines) {
        // if no addresses specified, simply return feature and value
        if (fasm_line.address_range.empty()) {
            tile_names_to_features[fasm_line.tile_name].emplace(fasm_line.feature, fasm_line.value_range.empty() || fasm_line.value_range.at(0) == 1);
        }
        // if addresses specified, iterate all of them, append each address to the feature, and assign the corresponding value
        else {
            for (u32 i = 0; i < fasm_line.address_range.size(); i++) {
                std::stringstream address;
                address << std::setw(2) << std::setfill('0') << std::dec << fasm_line.address_range.at(i);
                tile_names_to_features[fasm_line.tile_name].emplace(fasm_line.feature + "[" + address.str() + "]", fasm_line.value_range.at(i) == 1);
            }
        }
    }

    return tile_names_to_features;
}

bool FASM::to_file(const std::string& file_path) const
{
    std::ofstream out_file(file_path);
    if (!out_file) {
        std::cerr << "[ERROR] FASM: could not write to file at '" << file_path << "'." << std::endl;
        return false;
    }

    to_ostream(out_file);

    out_file.close();
    return true;
}

bool FASM::from_file(const std::string& file_path, bool overwrite)
{
    std::ifstream in_file(file_path);
    if (!in_file) {
        std::cerr << "[ERROR] FASM: could not read from file at '" << file_path << "'." << std::endl;
        return false;
    }

    if (overwrite) {
        m_fasm_lines.clear();
    }

    u32 line_number = 0;
    std::string line;
    while (std::getline(in_file, line)) {
        line_number++;
        line = utils::trim(line);

        // skip empty lines and comments
        if (line.empty() || line.at(0) == '#') {
            continue;
        }

        auto dot_pos = line.find(".");
        auto equals_pos = line.find("=", dot_pos);

        if (dot_pos == std::string::npos) {
            std::cerr << "[ERROR] FASM: invalid FASM code in line " << line_number << "." << std::endl;
            return false;
        }

        FASMLine fasm_line;
        fasm_line.tile_name = line.substr(0, dot_pos);

        // read name of tile
        std::string fasm_tile_name = line.substr(0, dot_pos);

        // has at least one address
        if (auto bracket_pos = line.find("[", dot_pos); bracket_pos != std::string::npos) {
            // read feature
            fasm_line.feature = utils::trim(line.substr(dot_pos + 1, bracket_pos - dot_pos - 1));

            // read feature address
            auto closing_pos = line.find("]", bracket_pos);
            if (closing_pos == std::string::npos) {
                std::cerr << "[ERROR] FASM: invalid address specification in line " << line_number << "." << std::endl;
                return false;
            }

            // has just a single address
            if (auto colon_pos = line.find(":", bracket_pos); colon_pos == std::string::npos) {
                try {
                    fasm_line.address_range.push_back(std::stoul(line.substr(bracket_pos + 1, closing_pos - bracket_pos - 1)));
                } catch (...) {
                    std::cerr << "[ERROR] FASM: could not read address of feature '" << fasm_line.feature << "' for tile '" << fasm_line.tile_name << "' in line " << line_number << "." << std::endl;
                    return false;
                }
            }
            // has a range of addresses
            else {
                try {
                    i32 start_address = std::stoul(line.substr(bracket_pos + 1, colon_pos - bracket_pos - 1));
                    i32 end_address = std::stoul(line.substr(colon_pos + 1, closing_pos - colon_pos - 1));
                    i32 direction = (start_address < end_address) ? 1 : -1;

                    for (i32 i = start_address; i != end_address + direction; i += direction) {
                        fasm_line.address_range.push_back(i);
                    }
                } catch (...) {
                    std::cerr << "[ERROR] FASM: could not read address of feature '" << fasm_line.feature << "' for tile '" << fasm_line.tile_name << "' in line " << line_number << "." << std::endl;
                    return false;
                }
            }
        }
        // has no address specified
        else {
            // read feature
            if (equals_pos == std::string::npos) {
                fasm_line.feature = utils::trim(line.substr(dot_pos + 1));
            } else {
                fasm_line.feature = utils::trim(line.substr(dot_pos + 1, equals_pos - dot_pos - 1));
            }
        }

        // read value
        if (equals_pos != std::string::npos) {
            std::string binary_string = utils::verilog_literal_to_binary(line.substr(equals_pos + 1));

            for (auto c : binary_string) {
                // convert to integer 0 and 1
                fasm_line.value_range.push_back((u32)(c - 48));
            }
        } else if (fasm_line.address_range.size() == 1) {
            // single address implicits to 1
            fasm_line.value_range.push_back(1);
        }

        if ((fasm_line.address_range.size() == fasm_line.value_range.size()) || fasm_line.address_range.empty()) {
            m_fasm_lines.emplace(fasm_line.tile_name + "." + fasm_line.feature, fasm_line);
        } else {
            std::cerr << "[ERROR] FASM: address range does not match value length of feature '" << fasm_line.feature << "' for tile '" << fasm_line.tile_name << "' in line " << line_number << "." << std::endl;
            return false;
        }
    }

    return true;
}

void FASM::print() const
{
    to_ostream(std::cout);
}

u32 FASM::size() const
{
    return m_fasm_lines.size();
}

void FASM::to_ostream(std::ostream& stream) const
{
    for (const auto& [target, fasm_line] : m_fasm_lines) {
        // if no address specified, simply write feature and value to file
        if (fasm_line.address_range.empty()) {
            stream << target;

            // only write value if it is unequal to '1'
            if (fasm_line.value_range.at(0) != 1) {
                stream << " = " << fasm_line.value_range.at(0);
            }

            stream << std::endl;
        }
        // if addresses specified, iterate all of them, append each address to the feature, and assign the corresponding value
        else {
            bool done = false;

            // special case: LUT initialization strings
            for (const SpecialCase& sc : m_special_cases) {
                if (target.substr(target.size() - sc.offset, sc.length) == sc.search_string) {
                    stream << target << "[" << (sc.bitlength - 1) << ":0] = " << sc.bitlength << "'h";

                    std::vector<u8> bitvector(sc.bitlength);
                    for (u32 i = 0; i < fasm_line.address_range.size(); i++) {
                        bitvector[fasm_line.address_range.at(i)] = fasm_line.value_range.at(i);
                    }

                    u32 val = 0;
                    for (i32 i = sc.bitlength - 1; i >= 0; --i) {
                        val |= bitvector[i] << (i % 4);
                        if (i % 4 == 0) {
                            stream << std::hex << val << std::dec;
                            val = 0;
                        }
                    }

                    stream << std::endl;

                    done = true;
                    break;
                }
            }

            if (done == false) {
                for (u32 i = 0; i < fasm_line.address_range.size(); i++) {
                    stream << target << "[" << fasm_line.address_range.at(i) << "]";

                    // only write value if it is unequal to '1'
                    if (fasm_line.value_range.at(i) != 1) {
                        stream << " = " << fasm_line.value_range.at(i);
                    }

                    stream << std::endl;
                }
            }
        }
    }
}
} // namespace bitstream
