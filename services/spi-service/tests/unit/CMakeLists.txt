# SPI Service Unit Tests

# Helper function to create test targets
function(add_spi_unit_test TEST_NAME)
    add_executable(${TEST_NAME} ${ARGN})

    target_link_libraries(${TEST_NAME}
        GTest::gtest_main
        GTest::gmock
        Threads::Threads
    )

    # Add mock sources if enabled
    if(ENABLE_MOCKS)
        target_sources(${TEST_NAME} PRIVATE
            ${CMAKE_CURRENT_SOURCE_DIR}/../mocks/mock_GPIO_driver.cpp
            ${CMAKE_CURRENT_SOURCE_DIR}/../mocks/mock_SPI_driver.cpp
        )
    endif()

    # Discover tests
    gtest_discover_tests(${TEST_NAME}
        PROPERTIES
        LABELS "unit;spi-service"
    )
endfunction()

# Define all unit test executables
add_spi_unit_test(test_GPIO_driver test_GPIO_driver.cpp)
add_spi_unit_test(test_SPI_driver test_SPI_driver.cpp)
add_spi_unit_test(test_I2C_driver test_I2C_driver.cpp)
add_spi_unit_test(test_FIFO_buffer test_FIFO_buffer.cpp)
add_spi_unit_test(test_ADS1293_lib test_ADS1293_lib.cpp)
add_spi_unit_test(test_ADS1293_process test_ADS1293_process.cpp)
add_spi_unit_test(test_MAX30009_lib test_MAX30009_lib.cpp)
add_spi_unit_test(test_MAX30009_process test_MAX30009_process.cpp)
add_spi_unit_test(test_MAX30009_MUX test_MAX30009_MUX.cpp)
add_spi_unit_test(test_MAX30009_calibration test_MAX30009_calibration.cpp)
add_spi_unit_test(test_WS2812_driver test_WS2812_driver.cpp)
add_spi_unit_test(test_WS2812_process test_WS2812_process.cpp)
add_spi_unit_test(test_error_handling test_error_handling.cpp)
add_spi_unit_test(test_state_machine test_state_machine.cpp)
