#include "programloader.h"

#include "common/endian.h"
#include "common/logging.h"
#include "simulator_exception.h"

#include <cerrno>
#include <cstring>
#include <exception>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

LOG_CATEGORY("machine.ProgramLoader");

// TODO - document
#ifndef O_BINARY
    #define O_BINARY 0
#endif

// EM_RISCV is not defined in libelfin's data.hh, so we define it here
// This is the official ELF machine type for RISC-V architecture
#ifndef EM_RISCV
    #define EM_RISCV 243
#endif

using namespace machine;

ProgramLoader::ProgramLoader(const QString &file) : elf_file(file) {
    // Open source file - option QIODevice::ExistingOnly cannot be used on Qt
    // <5.11
    if (!elf_file.open(QIODevice::ReadOnly | QIODevice::Unbuffered)) {
        throw SIMULATOR_EXCEPTION(
            Input,
            QString("Can't open input elf file for reading (") + QString(file)
                + QString(")"),
            std::strerror(errno));
    }

    // Create a file descriptor for the ELF file
    int fd = dup(elf_file.handle());
    if (fd < 0) {
        throw SIMULATOR_EXCEPTION(
            Input, "Failed to duplicate file descriptor", std::strerror(errno));
    }

    try {
        // Create mmap loader and parse ELF file
        loader = elf::create_mmap_loader(fd);
        elf_handle = elf::elf(loader);

        if (!elf_handle.valid()) {
            throw SIMULATOR_EXCEPTION(
                Input, "Invalid input file elf format, plain elf file expected",
                "");
        }

        const auto &hdr = elf_handle.get_hdr();

        executable_entry = Address(hdr.entry);

        // Check elf file format, executable expected, nothing else.
        if (hdr.type != elf::et::exec) {
            throw SIMULATOR_EXCEPTION(Input, "Invalid input file type", "");
        }

        // Check elf file architecture, of course only RISC-V is supported.
        if (hdr.machine != EM_RISCV) {
            throw SIMULATOR_EXCEPTION(Input, "Invalid input file architecture", "");
        }

        // Check elf file class, determine if 32bit or 64bit architecture.
        if (hdr.ei_class == elf::elfclass::_32) {
            LOG("Loaded executable: 32bit");
            architecture_type = ARCH32;
        } else if (hdr.ei_class == elf::elfclass::_64) {
            LOG("Loaded executable: 64bit");
            architecture_type = ARCH64;
            WARN("64bit simulation is not fully supported.");
        } else {
            WARN("Unsupported elf class: %d", (int)hdr.ei_class);
            throw SIMULATOR_EXCEPTION(
                Input,
                "Unsupported architecture type."
                "This simulator only supports 32bit and 64bit CPUs.",
                "");
        }
    } catch (const elf::format_error &e) {
        close(fd);
        throw SIMULATOR_EXCEPTION(
            Input, "ELF format error", e.what());
    } catch (const std::exception &e) {
        close(fd);
        throw SIMULATOR_EXCEPTION(
            Input, "Error loading ELF file", e.what());
    }
    // Note: fd is now owned by the mmap_loader and will be closed when the loader is destroyed
}

ProgramLoader::ProgramLoader(const char *file)
    : ProgramLoader(QString::fromLocal8Bit(file)) {}

ProgramLoader::~ProgramLoader() {
    // Close file
    elf_file.close();
}

void ProgramLoader::to_memory(Memory *mem) {
    // Load program to memory (just dump it byte by byte)
    for (const auto &seg : elf_handle.segments()) {
        const auto &phdr = seg.get_hdr();
        
        // Only load PT_LOAD segments
        if (phdr.type != elf::pt::load) {
            continue;
        }

        uint64_t base_address = phdr.vaddr;
        const char *seg_data = (const char *)seg.data();
        
        for (uint64_t i = 0; i < phdr.filesz; i++) {
            memory_write_u8(mem, base_address + i, (uint8_t)seg_data[i]);
        }
    }
}

Address ProgramLoader::end() {
    uint64_t last = 0;
    // Go through all segments and find out the last one
    for (const auto &seg : elf_handle.segments()) {
        const auto &phdr = seg.get_hdr();
        
        // Only consider PT_LOAD segments
        if (phdr.type != elf::pt::load) {
            continue;
        }
        
        uint64_t seg_end = phdr.vaddr + phdr.filesz;
        if (seg_end > last) {
            last = seg_end;
        }
    }
    return Address(last + 0x10); // We add offset so we are sure that also
                                 // pipeline is empty TODO propagate address
                                 // deeper
}

Address ProgramLoader::get_executable_entry() const {
    return executable_entry;
}

SymbolTable *ProgramLoader::get_symbol_table() {
    auto *p_st = new SymbolTable();

    try {
        for (const auto &sec : elf_handle.sections()) {
            const auto &shdr = sec.get_hdr();
            
            // Look for symbol table section
            if (shdr.type != elf::sht::symtab) {
                continue;
            }

            // Found symbol table
            auto symtab = sec.as_symtab();
            for (const auto &symbol : symtab) {
                const auto &sym_data = symbol.get_data();
                p_st->add_symbol(
                    symbol.get_name().c_str(),
                    sym_data.value,
                    sym_data.size,
                    (unsigned char)(((unsigned char)sym_data.binding() << 4) | (unsigned char)sym_data.type()),
                    (unsigned char)sym_data.other);
            }
            
            // We found the symbol table, no need to continue
            break;
        }
    } catch (const std::exception &e) {
        // If we can't read symbol table, just return empty one
        WARN("Failed to read symbol table from '%s': %s", 
             elf_file.fileName().toStdString().c_str(), e.what());
    }

    return p_st;
}

Endian ProgramLoader::get_endian() const {
    // Reading elf endian according to the ELF specs.
    const auto &hdr = elf_handle.get_hdr();
    if (hdr.ei_data == elf::elfdata::lsb) {
        return LITTLE;
    } else if (hdr.ei_data == elf::elfdata::msb) {
        return BIG;
    } else {
        throw SIMULATOR_EXCEPTION(
            Input,
            "ELF header e_ident malformed."
            "Unknown value of the byte EI_DATA."
            "Expected value little (=1) or big (=2).",
            "");
    }
}

ArchitectureType ProgramLoader::get_architecture_type() const {
    return architecture_type;
}
