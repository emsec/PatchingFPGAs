#pragma once

#include <memory>
#include <string>

namespace bitstream
{
    namespace utils
    {

        // TODO documentation
        class MemoryMappedFile
        {
        public:
            ~MemoryMappedFile();

            static std::unique_ptr<MemoryMappedFile> init_with_file(const std::string &path);

            void *const data() const { return data_; }
            const size_t size() const { return size_; }

        private:
            MemoryMappedFile(void *data, size_t size) : data_(data), size_(size){};

            void *data_;
            size_t size_;
        };

    } // namespace utils
} // namespace bitstream