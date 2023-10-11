#include "architecture/part.h"
#include "assembler/assembler.h"
#include "assembler/disassembler.h"
#include "assembler/fasm.h"
#include "configuration/bitstream.h"
#include "configuration/configuration.h"
#include "database/database.h"
#include "defines.h"
#include "utils/memory_mapped_file.h"

#include <gflags/gflags.h>

#include <iomanip>
#include <iostream>
#include <string>

DEFINE_string(o_fasm, "", "FASM file that the bitstream configuration is written to");
DEFINE_string(delta, "", "FASM file containing manipulations to the bitstream");
DEFINE_string(o_bitstream, "", "output file that the manipulated bitstream is written to");
DEFINE_string(packets, "", "file to write bitstream packets to before manipulation");

int main(int argc, char **argv)
{
    gflags::SetUsageMessage("Usage: bitstream [database directory] [device type] [bitstream file] [options]");
    gflags::ParseCommandLineFlags(&argc, &argv, true);

    std::string database_directory = argv[1];
    std::string device_type = argv[2];
    std::string bitstream_file = argv[3];

    std::set<std::string> supported_devices = {"xc7a35tcpg236-1", "xc7a35tcsg324-1", "xc7a35tftg256-1", "xc7a50tfgg484-1", "xc7a100tcsg324-1", "xc7a100tfgg676-1", "xc7a200tffg1156-1", "xc7a200tsbg484-1", "xc7k70tfbg676-2", "xc7z010clg400-1", "xc7z020clg400-1", "xc7z020clg484-1"};
    if (supported_devices.find(device_type) == supported_devices.end())
    {
        std::cerr << "[ERROR] Device type '" << device_type << "' is not supported." << std::endl;
        return 1;
    }

    std::string device_family;
    if (device_type.find("xc7a") == 0)
    {
        device_family = "artix7";
    }
    else if (device_type.find("xc7k") == 0)
    {
        device_family = "kintex7";
    }
    else if (device_family.find("xc7z") == 0)
    {
        device_family = "zynq7";
    }

    std::string device_database_directory = database_directory + "/" + device_family;

    std::string part_file = database_directory + "/" + device_family + "/" + device_type + "/part.yaml";

    auto bitstream = bitstream::Bitstream::from_file(bitstream_file);
    if (bitstream == nullptr)
    {
        std::cerr << "[ERROR] Bitstream: file '" << bitstream_file << "' not found or invalid." << std::endl;
        return 1;
    }

    auto part = bitstream::Part::from_file(part_file, device_type);
    if (part == nullptr)
    {
        std::cerr << "[ERROR] Part: file '" << part_file << "' not found or invalid." << std::endl;
        return 1;
    }

    auto config = bitstream::Configuration::from_bitstream(part, bitstream);
    if (config == nullptr)
    {
        std::cerr << "[ERROR] Configuration: unable to extract configuration from bitstream." << std::endl;
        return 1;
    }

    auto db = bitstream::Database::from_file(device_database_directory, *part);
    if (db == nullptr)
    {
        std::cerr << "[ERROR] Database: directory at '" << device_database_directory << "' not found or invalid." << std::endl;
        return 1;
    }

    if (!FLAGS_o_fasm.empty())
    {
        auto bitstream_fasm = std::make_shared<bitstream::FASM>();
        auto disassembler = std::make_shared<bitstream::Disassembler>(db);
        if (!disassembler->add_configuration_to_features(config, bitstream_fasm))
        {
            return 1;
        }
        if (!bitstream_fasm->to_file(FLAGS_o_fasm))
        {
            return 1;
        }
    }

    if (!FLAGS_packets.empty())
    {
        bitstream->packets_to_file(FLAGS_packets);
    }

    if (!FLAGS_delta.empty())
    {
        auto manipulations_fasm = std::make_shared<bitstream::FASM>();
        if (!manipulations_fasm->from_file(FLAGS_delta))
        {
            return 1;
        }

        auto assembler = std::make_shared<bitstream::Assembler>(db);
        if (!assembler->add_features_to_configuration(config, manipulations_fasm))
        {
            return 1;
        }

        if (!FLAGS_o_bitstream.empty())
        {
            bitstream = config->to_bitstream();
            if (!bitstream->to_file(FLAGS_o_bitstream))
            {
                return 1;
            }
        }
    }

    return 0;
}