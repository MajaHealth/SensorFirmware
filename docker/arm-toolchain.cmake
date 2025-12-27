# ARM64 Toolchain for Raspberry Pi CM4
# Cross-compilation configuration for 64-bit ARM (aarch64)

set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)

# Specify compilers
set(CMAKE_C_COMPILER aarch64-linux-gnu-gcc)
set(CMAKE_CXX_COMPILER aarch64-linux-gnu-g++)

# Search modes (use default paths for Debian cross-compilation)
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY BOTH)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE BOTH)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE BOTH)

# CM4 specific flags (Cortex-A72, 64-bit)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -mcpu=cortex-a72")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -mcpu=cortex-a72")

# Optimization flags
set(CMAKE_C_FLAGS_RELEASE "-O2 -DNDEBUG -ffunction-sections -fdata-sections")
set(CMAKE_CXX_FLAGS_RELEASE "-O2 -DNDEBUG -ffunction-sections -fdata-sections")

# Linker optimization
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,--gc-sections")
