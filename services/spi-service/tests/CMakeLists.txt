# SPI Service Tests CMakeLists.txt

# Test-specific configurations
if(ENABLE_MOCKS)
    add_definitions(-DUSE_MOCK_DRIVERS)
    message(STATUS "SPI Service tests: Using mock drivers")
endif()

# Include directories for tests
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/../include
    ${CMAKE_CURRENT_SOURCE_DIR}/../ADS1293_LIB
    ${CMAKE_CURRENT_SOURCE_DIR}/../MAX30009_LIB
    ${CMAKE_CURRENT_SOURCE_DIR}/../WS281x
    ${CMAKE_CURRENT_SOURCE_DIR}/../VTK
    ${CMAKE_CURRENT_SOURCE_DIR}/../hard_driver
    ${CMAKE_CURRENT_SOURCE_DIR}/mocks
)

# Add unit tests subdirectory (gtest)
if(BUILD_TESTS OR BUILD_UNIT_TESTS)
    add_subdirectory(unit)
endif()

# Add integration tests setup (pytest)
if(BUILD_TESTS OR BUILD_INTEGRATION_TESTS)
    # Configure pytest environment
    configure_file(
        ${CMAKE_CURRENT_SOURCE_DIR}/integration/pytest.ini.in
        ${CMAKE_CURRENT_BINARY_DIR}/integration/pytest.ini
        @ONLY
    )

    # Add pytest tests to CTest
    find_program(PYTEST_EXECUTABLE pytest)
    if(PYTEST_EXECUTABLE)
        add_test(
            NAME spi_service_integration_tests
            COMMAND ${PYTEST_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/integration
            WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        )
        set_tests_properties(spi_service_integration_tests PROPERTIES
            LABELS "integration;spi-service"
        )
    else()
        message(WARNING "pytest not found - integration tests will not be available")
    endif()
endif()
