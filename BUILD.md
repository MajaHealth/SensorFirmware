# Build Instructions

This document provides instructions for building the firmware services on a Raspberry Pi.

## Prerequisites

### Target Platform
- Raspberry Pi (ARM Linux, tested on Raspberry Pi OS)
- GCC/G++ compiler

### Install Required Dependencies

```bash
sudo apt update
sudo apt install -y build-essential libgpiod-dev libi2c-dev
```

## Building the Services

There are two independent services that need to be built separately.

---

## 1. Power Control Service

### Navigate to the directory
```bash
cd power_control_servise
```

### Create output directories
```bash
mkdir -p bin/Debug bin/Release obj/Debug obj/Release
```

### Debug Build
```bash
g++ -g -Wall -fexceptions \
    -Iinclude -Ihard_driver -IVTK -IWS281x \
    -o bin/Debug/power_control_servise \
    main.cpp PWRCNTR_process.cpp \
    -lgpiod -li2c
```

### Release Build
```bash
g++ -O2 -s -Wall -fexceptions \
    -Iinclude -Ihard_driver -IVTK -IWS281x \
    -o bin/Release/power_control_servise \
    main.cpp PWRCNTR_process.cpp \
    -lgpiod -li2c
```

---

## 2. SPI Device Service

### Navigate to the directory
```bash
cd SPI_DEV_servise
```

### Create output directories
```bash
mkdir -p bin/Debug bin/Release obj/Debug obj/Release
```

### Debug Build

First, compile the WS281x C library files:
```bash
gcc -g -Wall -c -IWS281x \
    WS281x/dma.c \
    WS281x/mailbox.c \
    WS281x/pcm.c \
    WS281x/pwm.c \
    WS281x/rpihw.c \
    WS281x/ws2811.c \
    -o obj/Debug/ws281x.o
```

Then compile and link the main application:
```bash
g++ -g -Wall -fexceptions \
    -Iinclude -Ihard_driver -IVTK -IADS1293_LIB -IMAX30009_LIB -IWS281x \
    -o bin/Debug/SPI_DEV_servise \
    main.cpp src/ADS1293_process.cpp src/MAX30009_process.cpp \
    WS281x/dma.c WS281x/mailbox.c WS281x/pcm.c WS281x/pwm.c WS281x/rpihw.c WS281x/ws2811.c \
    -lgpiod
```

### Release Build
```bash
g++ -O2 -s -Wall -fexceptions \
    -Iinclude -Ihard_driver -IVTK -IADS1293_LIB -IMAX30009_LIB -IWS281x \
    -o bin/Release/SPI_DEV_servise \
    main.cpp src/ADS1293_process.cpp src/MAX30009_process.cpp \
    WS281x/dma.c WS281x/mailbox.c WS281x/pcm.c WS281x/pwm.c WS281x/rpihw.c WS281x/ws2811.c \
    -lgpiod
```

---

## Using Makefiles (Recommended)

For easier building, you can create Makefiles in each service directory.

### Makefile for power_control_servise

Create `power_control_servise/Makefile`:
```makefile
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
```

### Makefile for SPI_DEV_servise

Create `SPI_DEV_servise/Makefile`:
```makefile
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
```

### Using the Makefiles

```bash
# Build debug version
make debug

# Build release version
make release

# Or just 'make' for release
make

# Clean build artifacts
make clean
```

---

## Building with Code::Blocks IDE

If you prefer using the Code::Blocks IDE:

1. Install Code::Blocks on the Raspberry Pi:
   ```bash
   sudo apt install codeblocks
   ```

2. Open the `.cbp` project file:
   - `power_control_servise/power_control_servise.cbp`
   - `SPI_DEV_servise/SPI_DEV_servise.cbp`

3. Select Build Target (Debug or Release) from the toolbar

4. Click Build (Ctrl+F9) or Build and Run (F9)

---

## Running the Services

After building, run the services with root privileges (required for GPIO and SPI access):

```bash
# Run Power Control Service
sudo ./power_control_servise/bin/Release/power_control_servise

# Run SPI Device Service (in another terminal)
sudo ./SPI_DEV_servise/bin/Release/SPI_DEV_servise
```

### Running as Systemd Services (Optional)

To run the services automatically at boot, create systemd service files.

Create `/etc/systemd/system/power_control.service`:
```ini
[Unit]
Description=Power Control Service
After=network.target

[Service]
Type=simple
ExecStart=/path/to/power_control_servise/bin/Release/power_control_servise
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/spi_dev.service`:
```ini
[Unit]
Description=SPI Device Service
After=network.target

[Service]
Type=simple
ExecStart=/path/to/SPI_DEV_servise/bin/Release/SPI_DEV_servise
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable power_control.service spi_dev.service
sudo systemctl start power_control.service spi_dev.service
```

---

## Verifying the Build

After running the services, verify they are listening on the correct ports:

```bash
# Check listening ports
netstat -tlnp | grep -E '501|1293|2812|30009'
```

Expected output should show:
- Port 501: Power Control Service
- Port 1293: ADS1293 ECG Service
- Port 2812: WS2812 LED Service
- Port 30009: MAX30009 Bioimpedance Service

---

## Troubleshooting

### Permission Denied Errors
- Run the services with `sudo`
- Ensure SPI is enabled: `sudo raspi-config` → Interface Options → SPI → Enable
- Ensure I2C is enabled: `sudo raspi-config` → Interface Options → I2C → Enable

### Library Not Found
```bash
# If libgpiod is not found
sudo apt install libgpiod-dev

# If libi2c is not found
sudo apt install libi2c-dev
```

### SPI Device Not Found
Check that SPI devices exist:
```bash
ls -la /dev/spidev0.*
```
If not present, enable SPI in `raspi-config` and reboot.
