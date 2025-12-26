# Power Service Unit Tests

function(add_power_unit_test TEST_NAME)
    add_executable(${TEST_NAME} ${ARGN})

    target_link_libraries(${TEST_NAME}
        GTest::gtest_main
        GTest::gmock
        Threads::Threads
    )

    if(ENABLE_MOCKS)
        target_sources(${TEST_NAME} PRIVATE
            ${CMAKE_CURRENT_SOURCE_DIR}/../mocks/mock_SMBus_driver.cpp
            ${CMAKE_CURRENT_SOURCE_DIR}/../mocks/mock_GPIO_driver.cpp
        )
    endif()

    gtest_discover_tests(${TEST_NAME}
        PROPERTIES
        LABELS "unit;power-service"
    )
endfunction()

# Define test executables
add_power_unit_test(test_power_control test_power_control.cpp)
add_power_unit_test(test_battery_monitor test_battery_monitor.cpp)
add_power_unit_test(test_SMBus_driver test_SMBus_driver.cpp)
