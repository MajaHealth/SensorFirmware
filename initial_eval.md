I completed a read-only review of the MAX30009 datasheet, EV kit manual, and the local implementation. No files were changed.

**Sources Read**
- Datasheets: [max30009.pdf](c:/Users/delphic/Documents/MajaHealth/SensorFirmware/datasheet/max30009.pdf), [max30009evkit.pdf](c:/Users/delphic/Documents/MajaHealth/SensorFirmware/datasheet/max30009evkit.pdf)
- Core implementation: [MAX30009_process.cpp](c:/Users/delphic/Documents/MajaHealth/SensorFirmware/SPI_DEV_servise/src/MAX30009_process.cpp:42), [max30009_lib.h](c:/Users/delphic/Documents/MajaHealth/SensorFirmware/SPI_DEV_servise/MAX30009_LIB/max30009_lib.h:858), [max30009_data_struct.h](c:/Users/delphic/Documents/MajaHealth/SensorFirmware/SPI_DEV_servise/MAX30009_LIB/max30009_data_struct.h:13), [max30009_register_struct.h](c:/Users/delphic/Documents/MajaHealth/SensorFirmware/SPI_DEV_servise/MAX30009_LIB/max30009_register_struct.h:9)

**MAX30009 Mental Model**
- The MAX30009 is a BioZ AFE with a stimulus TX path, differential RX path, I/Q demodulation, dual 20-bit ADC outputs, FIFO, flexible electrode MUX, lead bias, lead-off detection, and calibration support.
- Current-drive BioZ is the main mode used here. The chip generates a sine-wave current from `16nA RMS` to `1.28mA RMS`, with frequency-dependent safety lockouts.
- The receive path measures `BIP - BIN`, demodulates into in-phase `I` and quadrature `Q`, filters/decimates, and pushes tagged 24-bit FIFO words.
- FIFO words are 4-bit tag + 20-bit signed data. Tag `0x1` is I, tag `0x2` is Q, marker is `0xFFFFFE`, invalid/empty is `0xFFFFFF`.
- Clocking is PLL-based: `REF_CLK -> PLL_CLK -> BIOZ_SYNTH_CLK/BIOZ_ADC_CLK -> stimulus frequency/sample rate`. The datasheet requires `PLL_CLK` 14-28MHz, `BIOZ_ADC_CLK` 16-36.375kHz, and the stimulus/sample-rate ratio must be `0.5` or an integer.

**Firmware Architecture**
- `main.cpp` starts three JSON TCP servers: ADS1293 on `1293`, MAX30009 on `30009`, WS2812 on `2812`, then runs a 500us polling loop.
- MAX30009 uses `/dev/spidev0.0` at 5MHz through `SPI_hard_driver_cls`.
- GPIOs are Raspberry Pi/libgpiod lines: MUX relay lines `17, 6, 27, 13, 26`, calibration/work select `19`, and MAX30009 power `21`.
- The MAX30009 process layer owns the measurement state machine, calibration state machine, JSON command handling, and FIFO drain.
- The lower library is a register-shadow driver: setters update packed bitfield structs, write one-byte MAX30009 registers, then read back to verify.

**Measurement Flow**
- A JSON `"settings"` command with `"measure_enable": true` moves the state machine into pre-measurement.
- Pre-measurement uses the base calibration table at the nearest indexed frequency, with fixed `64uA`, gain `x10`, bypass filters, and a target 1000Hz measure rate.
- It takes 20 averaged I/Q FIFO pairs, converts/calibrates them, and uses `Load_real` as `pre_meas_impendace_value`.
- The firmware then chooses a calibration resistor near that impedance via the external relay ladder, picks an auto gain, calibrates at the requested frequency/current, and finally starts continuous measurement.
- Continuous measurement configures internal 32.768kHz REF clock, high amplifier range/bandwidth, external cap enabled, DC restore enabled, drive OOR enabled, internal/external input-load compensation enabled, 4-electrode MUX mapping, 50M lead bias, fast-start, selected gain/current/frequency, then enables PLL and both I/Q channels.

**Calibration And Math**
- The calibration state machine mirrors the datasheet: offset measurement, in-phase RCAL measurement, quadrature RCAL measurement, then magnitude/phase coefficients.
- Base calibration table: [base_table.json](c:/Users/delphic/Documents/MajaHealth/SensorFirmware/SPI_DEV_servise/base_table.json) has 100 entries from 1kHz to 500kHz.
- External relay calibration range is 32 discrete values from `47Ω` to `1131Ω`; the requested resistor is rounded to the closest available value.
- Raw ADC is converted using the datasheet sine demodulation scale: denominator `2^19 * 2/pi ≈ 333772`, gain, and peak current. The library stores impedance in centi-ohms, then divides by 100 for user-level ohms.
- Output JSON returns decimated calibrated samples as `[real, mag, imag, angle, overload]`, scaled by `10000`, plus `data_frequency` and timestamp.

**Important Observations**
- `set_drive_frequency()` appears to have a real bug: `BIOZ_CH_FSEL` is set to `1` in both branches, but the datasheet says set it to `1` only when `F_BIOZ == BIOZ_ADC_CLK / 8`, otherwise `0`. See [max30009_lib.h](c:/Users/delphic/Documents/MajaHealth/SensorFirmware/SPI_DEV_servise/MAX30009_LIB/max30009_lib.h:1023).
- FIFO sign extension is suspicious. The 20-bit two’s-complement conversion uses complement-minus-one logic and is wrong near negative full-scale/near-zero negative values. Correct handling should sign-extend or subtract `1 << 20`. See [max30009_lib.h](c:/Users/delphic/Documents/MajaHealth/SensorFirmware/SPI_DEV_servise/MAX30009_LIB/max30009_lib.h:1927).
- The datasheet recommends enabling PLL, waiting for lock, then enabling BioZ I/Q. The code enables PLL and immediately enables I/Q without checking lock. See [MAX30009_process.cpp](c:/Users/delphic/Documents/MajaHealth/SensorFirmware/SPI_DEV_servise/src/MAX30009_process.cpp:470).
- Calibration follows the main datasheet sequence, but there is a datasheet note saying offsets should be calculated at intended current, while the code measures offset at `16nA`. This may affect absolute accuracy.
- Low-frequency GSR/EDA support is incomplete from a calibration perspective: the base table clamps below 1kHz to index 0, even though the chip supports down to 16Hz.
- The external calibration ladder only covers roughly 47-1131Ω, so higher body/electrode impedance measurements will calibrate against the nearest endpoint, not a matched RCAL.
- The implementation is built around tetrapolar BIA/BIS-style routing: `DRVP=EL1`, `BIP=EL2B`, `BIN=EL3B`, `DRVN=EL4`, with EL2A/EL3A used as guard-capable nodes per the EV kit guidance.

Overall: the firmware has a coherent MAX30009 architecture and a serious attempt at proper absolute BioZ calibration, including frequency-indexed base calibration and per-measurement work calibration. The highest-priority technical cleanup would be the `BIOZ_CH_FSEL` branch, FIFO sign extension, and explicit PLL-lock/startup sequencing.