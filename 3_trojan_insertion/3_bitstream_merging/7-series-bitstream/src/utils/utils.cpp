#include "utils/utils.h"
#include "defines.h"

#include <algorithm>
#include <iostream>
#include <iterator>
#include <map>
#include <sstream>
#include <string>
#include <vector>

namespace bitstream
{
    namespace utils
    {
        bool begins_with(const std::string &str, const std::string &begin)
        {
            if (begin.size() > str.size())
            {
                return false;
            }

            return std::equal(begin.begin(), begin.end(), str.begin());
        }

        bool ends_with(const std::string &str, const std::string &end)
        {
            if (end.size() > str.size())
            {
                return false;
            }

            return std::equal(end.rbegin(), end.rend(), str.rbegin());
        }

        std::string to_lower(const std::string &str)
        {
            std::string res = str;

            std::transform(str.begin(), str.end(), res.begin(), [](unsigned char c) { return std::tolower(c); });

            return res;
        }

        std::string to_upper(const std::string &str)
        {
            std::string res = str;

            std::transform(str.begin(), str.end(), res.begin(), [](unsigned char c) { return std::toupper(c); });

            return res;
        }

        std::vector<std::string> split(const std::string &str, const char delim)
        {
            std::vector<std::string> res;
            std::string item = "";
            std::stringstream ss(str);

            while (std::getline(ss, item, delim))
            {
                res.push_back(item);
            }

            if (str.back() == delim)
            {
                res.push_back("");
            }
            return res;
        }

        std::string trim(const std::string &str, const std::string &to_remove)
        {
            size_t start = str.find_first_not_of(to_remove);
            size_t end = str.find_last_not_of(to_remove);

            if (start != std::string::npos)
            {
                return str.substr(start, end - start + 1);
            }
            else
            {
                return "";
            }
        }

        std::string join(const std::vector<std::string> &parts, const std::string delim)
        {
            std::stringstream ss;
            bool first = true;

            for (auto it = parts.begin(); it != parts.end(); ++it)
            {
                if (!first)
                {
                    ss << delim;
                }
                first = false;
                ss << *it;
            }

            return ss.str();
        }

        bool is_integer(const std::string &str)
        {
            return !str.empty() && std::find_if(str.begin(), str.end(), [](unsigned char c) { return !std::isdigit(c); }) == str.end();
        }

        namespace
        {
            static const std::map<char, std::string> oct_to_bin = {{'0', "000"}, {'1', "001"}, {'2', "010"}, {'3', "011"}, {'4', "100"}, {'5', "101"}, {'6', "110"}, {'7', "111"}};
            static const std::map<char, std::string> hex_to_bin = {{'0', "0000"},
                                                                   {'1', "0001"},
                                                                   {'2', "0010"},
                                                                   {'3', "0011"},
                                                                   {'4', "0100"},
                                                                   {'5', "0101"},
                                                                   {'6', "0110"},
                                                                   {'7', "0111"},
                                                                   {'8', "1000"},
                                                                   {'9', "1001"},
                                                                   {'a', "1010"},
                                                                   {'b', "1011"},
                                                                   {'c', "1100"},
                                                                   {'d', "1101"},
                                                                   {'e', "1110"},
                                                                   {'f', "1111"}};
        } // namespace

        std::string verilog_literal_to_binary(const std::string &literal)
        {
            const auto value = to_lower(trim(literal));

            i32 len = -1;
            std::string prefix;
            std::string number;
            std::string res;

            // base specified?
            if (value.find('\'') == std::string::npos)
            {
                prefix = "d";
                number = value;
            }
            else
            {
                if (value.at(0) != '\'')
                {
                    len = std::stoi(value.substr(0, value.find('\'')));
                }
                prefix = value.substr(value.find('\'') + 1, 1);
                number = value.substr(value.find('\'') + 2);
            }

            // select base
            switch (prefix.at(0))
            {
            case 'b':
            {
                for (const auto &c : number)
                {
                    if (c >= '0' && c <= '1')
                    {
                        res += c;
                    }
                    else
                    {
                        std::cerr << "[ERROR] Utils: invalid character within binary literal " << value << "." << std::endl;
                        return "";
                    }
                }
                break;
            }

            case 'o':
                for (const auto &c : number)
                {
                    if (c >= '0' && c <= '7')
                    {
                        res += oct_to_bin.at(c);
                    }
                    else
                    {
                        std::cerr << "[ERROR] Utils: invalid character within octal literal " << value << "." << std::endl;
                        return "";
                    }
                }
                break;

            case 'd':
            {
                u64 tmp_val = 0;

                for (const auto &c : number)
                {
                    if (c >= '0' && c <= '9')
                    {
                        tmp_val = (tmp_val * 10) + (c - '0');
                    }
                    else
                    {
                        std::cerr << "[ERROR] Utils: invalid character within decimal literal " << value << "." << std::endl;
                        return "";
                    }
                }

                do
                {
                    res = (((tmp_val & 1) == 1) ? "1" : "0") + res;
                    tmp_val >>= 1;
                } while (tmp_val != 0);
                break;
            }

            case 'h':
            {
                for (const auto &c : number)
                {
                    if ((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))
                    {
                        res += hex_to_bin.at(c);
                    }
                    else
                    {
                        std::cerr << "[ERROR] Utils: invalid character within hexadecimal literal " << value << "." << std::endl;
                        return "";
                    }
                }
                break;
            }

            default:
            {
                std::cerr << "[ERROR] Utils: invalid base within number literal " << value << ":";
                return "";
            }
            }

            if (len != -1)
            {
                // fill with '0'
                for (i32 i = 0; i < len - (i32)res.size(); i++)
                {
                    res = "0" + res;
                }
            }

            return res;
        }

    } // namespace utils
} // namespace bitstream