# SPI Service CMakeLists.txt
cmake_minimum_required(VERSION 3.18)

project(spi-service VERSION 1.0.0 LANGUAGES C CXX)

message(STATUS "Configuring SPI Service...")

# Service-specific settings
set(SERVICE_NAME spi-service)
set(SERVICE_PORT_ADS1293 1293)
set(SERVICE_PORT_MAX30009 30009)
set(SERVICE_PORT_WS2812 2812)

# Source files
set(SPI_SERVICE_SOURCES
    src/main.cpp
    src/ADS1293_process.cpp
    src/MAX30009_process.cpp
)

# WS281x library sources (C files)
set(WS281X_SOURCES
    WS281x/dma.c
    WS281x/mailbox.c
    WS281x/pcm.c
    WS281x/pwm.c
    WS281x/rpihw.c
    WS281x/ws2811.c
)

# Include directories
set(SPI_SERVICE_INCLUDES
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/hard_driver
    ${CMAKE_CURRENT_SOURCE_DIR}/ADS1293_LIB
    ${CMAKE_CURRENT_SOURCE_DIR}/MAX30009_LIB
    ${CMAKE_CURRENT_SOURCE_DIR}/VTK
    ${CMAKE_CURRENT_SOURCE_DIR}/WS281x
)

# Create WS281x static library
add_library(ws281x STATIC ${WS281X_SOURCES})
target_include_directories(ws281x PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/WS281x)
target_compile_options(ws281x PRIVATE -Wall -Wextra)

# Create the executable
add_executable(${SERVICE_NAME} ${SPI_SERVICE_SOURCES})

# Include directories for the service
target_include_directories(${SERVICE_NAME} PRIVATE ${SPI_SERVICE_INCLUDES})

# Link libraries
target_link_libraries(${SERVICE_NAME} 
    PRIVATE 
        ws281x
        Threads::Threads
        rt
        m
)

# Compiler definitions
target_compile_definitions(${SERVICE_NAME} PRIVATE
    SERVICE_NAME="${SERVICE_NAME}"
    ADS1293_PORT=${SERVICE_PORT_ADS1293}
    MAX30009_PORT=${SERVICE_PORT_MAX30009}
    WS2812_PORT=${SERVICE_PORT_WS2812}
)

# Set specific compile options
target_compile_options(${SERVICE_NAME} PRIVATE
    -pthread
    $<$<CONFIG:Release>:-O2 -DNDEBUG>
    $<$<CONFIG:Debug>:-O0 -g3 -DDEBUG>
)

# Set linker options
set_target_properties(${SERVICE_NAME} PROPERTIES
    LINK_FLAGS "-pthread"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)

# Install target
install(TARGETS ${SERVICE_NAME}
    RUNTIME DESTINATION /opt/sensor-firmware/bin
    COMPONENT spi-service
)

# Install calibration files
install(DIRECTORY calib/
    DESTINATION /opt/sensor-firmware/calib
    FILES_MATCHING PATTERN "*.json"
    COMPONENT spi-service
)

# Post-build: Generate hash
add_custom_command(TARGET ${SERVICE_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E echo "Generating hash for ${SERVICE_NAME}..."
    COMMAND sha256sum $<TARGET_FILE:${SERVICE_NAME}> > $<TARGET_FILE:${SERVICE_NAME}>.sha256
    COMMENT "Generating SHA256 hash for artifact integrity"
    VERBATIM
)

# Print configuration
message(STATUS "  Binary: ${SERVICE_NAME}")
message(STATUS "  Ports: ADS1293=${SERVICE_PORT_ADS1293}, MAX30009=${SERVICE_PORT_MAX30009}, WS2812=${SERVICE_PORT_WS2812}")
message(STATUS "  Sources: ${CMAKE_CURRENT_LIST_DIR}/src/")
message(STATUS "  Output: ${CMAKE_BINARY_DIR}/bin/${SERVICE_NAME}")