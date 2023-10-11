#pragma once

#include <string>
#include <vector>

namespace bitstream
{
    namespace utils
    {
        /**
         * Returns true if the given string begins with the specified begin sequence.
         *
         * @param[in] str - The string to operate on.
         * @param[in] begin - The begin sequence.
         * @returns True if the string begins with the specified sequence, false otherwise.
         */
        bool begins_with(const std::string &str, const std::string &begin);

        /**
         * Returns true if the given string ends with the specified end sequence.
         *
         * @param[in] str - The string to operate on.
         * @param[in] end - The end sequence.
         * @returns True if the string ends with the specified sequence, false otherwise.
         */
        bool ends_with(const std::string &str, const std::string &end);

        /**
         * Transforms a string to only contain lowercase letters.
         *
         * @param[in] str - The string to operate on.
         * @returns The resulting lowercase string.
         */
        std::string to_lower(const std::string &str);

        /**
         * Transforms a string to only contain uppercase letters.
         *
         * @param[in] str - The string to operate on.
         * @returns The resulting uppercase string.
         */
        std::string to_upper(const std::string &str);

        /**
         * Splits a string into a vector of strings using the specified delimiter.
         *
         * @param[in] str - The string to operate on.
         * @param[in] delim - The delimiter.
         * @returns The parts of the string as a vector.
         */
        std::vector<std::string> split(const std::string &str, const char delim);

        /**
         * Joins a vector of strings into single string using the specified delimiter.
         *
         * @param[in] parts - The vector of strings to operate on.
         * @param[in] delim - The delimiter.
         * @returns The joined string.
         */
        std::string join(const std::vector<std::string> &parts, const std::string delim);

        /**
         * Removes whitespace characters at both ends of a string.
         *
         * @param[in] str - The string to operate on.
         * @param[in] to_remove - Characters that should be removed.
         * @returns The trimmed string.
         */
        std::string trim(const std::string &str, const std::string &to_remove = " \t\r\n");

        /**
         * Determines whether the given string represents an integer.
         * 
         * @param[in] str - The string to operate on.
         * @returns True if the string represents an integer, false otherwise.
         */
        bool is_integer(const std::string &str);

        /**
         * Converts a verilog number literal into a string of binary values.
         * 
         * @param[in] literal - The number literal.
         * @returns The binary string.
         */
        std::string verilog_literal_to_binary(const std::string &literal);

    } // namespace utils
} // namespace bitstream