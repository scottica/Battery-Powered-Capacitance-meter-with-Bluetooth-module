# STM32 Wireless BLE Capacitance Meter

An end-to-end embedded system that measures unknown capacitance values with high precision and streams the data wirelessly to a PC via Bluetooth Low Energy (BLE). 

This project consists of **bare-metal C firmware** running on an ARM Cortex-M0+ (STM32L051xx) and an **asynchronous Python logging script** that parses the incoming BLE telemetry into a structured CSV file for data analysis.

## 🚀 Key Features

* **Wireless Data Logging:** A custom asynchronous Python script (`bleak` library) connects over BLE to automatically log live capacitance data and unit prefixes into a structured CSV file.
* **Precision Period Measurement:** Leverages the STM32's 24-bit `SysTick` timer running at 32 MHz to average 100 continuous waveform periods, ensuring highly stable and accurate capacitance calculations.
* **Smart Power Management:** Integrates an infrared (IR) proximity sensor to detect user presence, automatically entering a low-power "Smart Sleep" state (disabling the LCD and indicators) to conserve battery when unattended.
* **Rolling History Array:** Stores up to 10 stable capacitance readings in memory, accessible via an interactive LCD menu. Includes a "Smart Export" feature to automatically dump the history block over Bluetooth when the array fills up.
* **Auto-Ranging & Dynamic UI:** Features dedicated hardware interrupts for instantly toggling between nanoFarads (nF) and microFarads (uF), complete with an interactive options menu and multi-color LED status indicators.
* **Hardware-to-PC Control:** Allows the user to remotely wipe the PC-side Excel/CSV log directly from a physical hardware push-button on the STM32 device.

## 🧮 How It Works

The system utilizes an astable multivibrator circuit (like a 555 timer) where the unknown capacitor dictates the oscillation frequency. The square wave output is fed into pin `PA8` on the STM32. 

The firmware polls the 24-bit `SysTick` timer to measure the period (T) of the incoming square wave. It averages 100 periods to filter out noise, and then calculates the capacitance based on the resistor values in the hardware circuit (R1 = 1k Ohm, R2 = 1k Ohm):

C = (1.44 * T) / (R1 + 2 * R2)

## 🛠️ Hardware Requirements

* **Microcontroller:** STM32L051xx (ARM Cortex-M0+)
* **Wireless:** Bluetooth Low Energy (BLE) UART Module (e.g., AT-09, HM-10)
* **Display:** 16x2 Character LCD (4-bit mode)
* **Sensors:** IR Proximity Sensor
* **Circuitry:** 555 Timer IC (configured in astable mode), 1k Ohm resistors
* **I/O:** 6x Push Buttons, 1x RGB LED (or 3x individual LEDs)

## 💻 Tech Stack

* **Embedded Firmware:** Bare-metal C, STM32 CMSIS
* **Timers/Interrupts:** `SysTick` (Period Measurement), `TIM2` (1ms System Tick), `EXTI`/`NVIC` (Hardware Button Interrupts)
* **PC Software:** Python 3.x
* **Python Libraries:** `asyncio`, `bleak` (Bluetooth Low Energy), `os`

## ⚙️ Installation & Setup

### 1. Firmware Flashing
1. Open the project in your preferred STM32 IDE (e.g., Keil uVision, STM32CubeIDE).
2. Ensure the target MCU is set to `STM32L051xx`.
3. Build the project and flash it to the board via ST-LINK.

### 2. Python Environment Setup
Navigate to the PC software directory and install the required asynchronous Bluetooth library:
`pip install bleak asyncio`

### 3. BLE Configuration
In the Python script (`logger.py`), ensure the MAC address matches your specific BLE module:
`address = "B0:B1:13:2D:55:D0"`
`UART_RX_CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"`

## 📊 Usage Instructions

1. **Power On:** Turn on the STM32 system. The LCD will display "Capacitance".
2. **Start Logger:** Run the Python script on your PC:
   `python logger.py`
3. **Measure:** Insert a capacitor into the oscillator circuit. The STM32 will calculate the value, display it on the LCD, and instantly transmit it to the PC.
4. **Log Data:** The Python script will output the live data to the terminal and append it to `capacitance_data.csv`.
5. **Clear Log:** Press the physical "Clear Export" button on the device to send a command that tells the Python script to wipe the CSV file clean.
