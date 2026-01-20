CXX = g++
CXXFLAGS = -Wall -fexceptions
INCLUDES = -Iinclude -Ihard_driver -IVTK -IWS281x
LIBS = -lgpiod -li2c

SOURCES = main.cpp PWRCNTR_process.cpp
TARGET_DEBUG = bin/Debug/power_control_servise
TARGET_RELEASE = bin/Release/power_control_servise

.PHONY: all debug release clean dirs

all: release

dirs:
	mkdir -p bin/Debug bin/Release obj/Debug obj/Release

debug: dirs
	$(CXX) -g $(CXXFLAGS) $(INCLUDES) -o $(TARGET_DEBUG) $(SOURCES) $(LIBS)

release: dirs
	$(CXX) -O2 -s $(CXXFLAGS) $(INCLUDES) -o $(TARGET_RELEASE) $(SOURCES) $(LIBS)

clean:
	rm -rf bin obj
