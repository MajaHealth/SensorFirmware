CXX = g++
CC = gcc
CXXFLAGS = -Wall -fexceptions
CFLAGS = -Wall
INCLUDES = -Iinclude -Ihard_driver -IVTK -IADS1293_LIB -IMAX30009_LIB -IWS281x
LIBS = -lgpiod

CPP_SOURCES = main.cpp src/ADS1293_process.cpp src/MAX30009_process.cpp
C_SOURCES = WS281x/dma.c WS281x/mailbox.c WS281x/pcm.c WS281x/pwm.c WS281x/rpihw.c WS281x/ws2811.c

TARGET_DEBUG = bin/Debug/SPI_DEV_servise
TARGET_RELEASE = bin/Release/SPI_DEV_servise

.PHONY: all debug release clean dirs

all: release

dirs:
	mkdir -p bin/Debug bin/Release obj/Debug obj/Release

debug: dirs
	$(CXX) -g $(CXXFLAGS) $(INCLUDES) -o $(TARGET_DEBUG) $(CPP_SOURCES) $(C_SOURCES) $(LIBS)

release: dirs
	$(CXX) -O2 -s $(CXXFLAGS) $(INCLUDES) -o $(TARGET_RELEASE) $(CPP_SOURCES) $(C_SOURCES) $(LIBS)

clean:
	rm -rf bin obj
