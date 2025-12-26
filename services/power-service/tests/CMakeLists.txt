# Power Service Tests CMakeLists.txt

if(ENABLE_MOCKS)
    add_definitions(-DUSE_MOCK_DRIVERS)
    message(STATUS "Power Service tests: Using mock drivers")
endif()

# Include directories
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/../include
    ${CMAKE_CURRENT_SOURCE_DIR}/../VTK
    ${CMAKE_CURRENT_SOURCE_DIR}/../hard_driver
    ${CMAKE_CURRENT_SOURCE_DIR}/mocks
)

# Add unit tests
if(BUILD_TESTS OR BUILD_UNIT_TESTS)
    add_subdirectory(unit)
endif()

# Add integration tests (pytest)
if(BUILD_TESTS OR BUILD_INTEGRATION_TESTS)
    find_program(PYTEST_EXECUTABLE pytest)
    if(PYTEST_EXECUTABLE)
        add_test(
            NAME power_service_integration_tests
            COMMAND ${PYTEST_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/integration
            WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        )
        set_tests_properties(power_service_integration_tests PROPERTIES
            LABELS "integration;power-service"
        )
    endif()
endif()
