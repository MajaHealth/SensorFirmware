# Power Service CMakeLists.txt
cmake_minimum_required(VERSION 3.18)

project(power-service VERSION 1.0.0 LANGUAGES CXX)

message(STATUS "Configuring Power Control Service...")

# Service-specific settings
set(SERVICE_NAME power-service)
set(SERVICE_PORT 501)

# Source files
set(POWER_SERVICE_SOURCES
    src/main.cpp
    src/PWRCNTR_process.cpp
)

# Include directories
set(POWER_SERVICE_INCLUDES
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/hard_driver
    ${CMAKE_CURRENT_SOURCE_DIR}/VTK
)

# Create the executable
add_executable(${SERVICE_NAME} ${POWER_SERVICE_SOURCES})

# Include directories for the service
target_include_directories(${SERVICE_NAME} PRIVATE ${POWER_SERVICE_INCLUDES})

# Link libraries
target_link_libraries(${SERVICE_NAME}
    PRIVATE
        Threads::Threads
        gpiod
        i2c
        rt
        m
)

# Compiler definitions
target_compile_definitions(${SERVICE_NAME} PRIVATE
    SERVICE_NAME="${SERVICE_NAME}"
    PWRCNTR_PORT=${SERVICE_PORT}
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
    COMPONENT power-service
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
message(STATUS "  Port: ${SERVICE_PORT}")
message(STATUS "  Sources: ${CMAKE_CURRENT_LIST_DIR}/src/")
message(STATUS "  Output: ${CMAKE_BINARY_DIR}/bin/${SERVICE_NAME}")