cmake_minimum_required(VERSION 3.18)

# Read version from VERSION file
file(READ "${CMAKE_CURRENT_SOURCE_DIR}/VERSION" VERSION_STRING)
string(STRIP "${VERSION_STRING}" VERSION_STRING)

project(SensorFirmware 
    VERSION ${VERSION_STRING}
    LANGUAGES C CXX
)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Build type
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

message(STATUS "========================================")
message(STATUS "  Sensor Firmware Build Configuration")
message(STATUS "========================================")
message(STATUS "Project: ${PROJECT_NAME}")
message(STATUS "Version: ${PROJECT_VERSION}")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "C Standard: ${CMAKE_C_STANDARD}")

# Platform detection
if(CMAKE_CROSSCOMPILING)
    message(STATUS "Cross-compiling for: ${CMAKE_SYSTEM_PROCESSOR}")
    message(STATUS "Toolchain: ${CMAKE_TOOLCHAIN_FILE}")
else()
    message(STATUS "Native build for: ${CMAKE_SYSTEM_PROCESSOR}")
endif()

message(STATUS "========================================")

# Compiler flags for reproducible builds
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Wextra")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra")

# Release optimizations
set(CMAKE_C_FLAGS_RELEASE "-O2 -DNDEBUG")
set(CMAKE_CXX_FLAGS_RELEASE "-O2 -DNDEBUG")

# Debug flags
set(CMAKE_C_FLAGS_DEBUG "-O0 -g3 -DDEBUG")
set(CMAKE_CXX_FLAGS_DEBUG "-O0 -g3 -DDEBUG")

# Set output directories
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# Find required packages
find_package(Threads REQUIRED)

# Common include directories
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}
)

# Enable testing
enable_testing()

# Add subdirectories for services
add_subdirectory(services/spi-service)
add_subdirectory(services/power-service)

# Custom target for hash generation
add_custom_target(generate-hashes
    COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/scripts/generate-hashes.sh ${CMAKE_BINARY_DIR}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Generating artifact hashes for verification"
    VERBATIM
)

# Custom target for SBOM generation
add_custom_target(generate-sbom
    COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/scripts/generate-sbom.sh ${CMAKE_BINARY_DIR}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Generating Software Bill of Materials (SBOM)"
    VERBATIM
)

# Install rules
install(DIRECTORY config/ 
    DESTINATION /opt/sensor-firmware/config
    FILES_MATCHING PATTERN "*.json" PATTERN "*.conf"
)

# Print build summary
add_custom_target(build-summary ALL
    COMMAND ${CMAKE_COMMAND} -E echo ""
    COMMAND ${CMAKE_COMMAND} -E echo "=========================================="
    COMMAND ${CMAKE_COMMAND} -E echo "  Build Summary"
    COMMAND ${CMAKE_COMMAND} -E echo "=========================================="
    COMMAND ${CMAKE_COMMAND} -E echo "Output Directory: ${CMAKE_BINARY_DIR}/bin"
    COMMAND ${CMAKE_COMMAND} -E echo "Services built:"
    COMMAND ${CMAKE_COMMAND} -E echo "  - spi-service"
    COMMAND ${CMAKE_COMMAND} -E echo "  - power-service"
    COMMAND ${CMAKE_COMMAND} -E echo "=========================================="
    COMMAND ${CMAKE_COMMAND} -E echo ""
    VERBATIM
)

# CPack configuration for packaging
set(CPACK_PACKAGE_NAME "${PROJECT_NAME}")
set(CPACK_PACKAGE_VERSION "${PROJECT_VERSION}")
set(CPACK_PACKAGE_VENDOR "Your Company")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "Sensor Firmware for CM4")
set(CPACK_GENERATOR "TGZ")

include(CPack)