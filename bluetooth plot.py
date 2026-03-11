import asyncio
import os
from bleak import BleakClient

address = "B0:B1:13:2D:55:D0" 
UART_RX_CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
CSV_FILENAME = 'capacitance_data.csv'

data_buffer = ""

if not os.path.isfile(CSV_FILENAME):
    with open(CSV_FILENAME, 'w') as f:
        f.write("Capacitance (Value),Unit\n")

def process_complete_line(line):
    global data_buffer
    clean_line = line.strip()
    if not clean_line: return

    if clean_line == 'C':
        with open(CSV_FILENAME, 'w') as f:
            f.write("Capacitance (Value),Unit\n")
        print("\n[CSV Cleared]", flush=True)
        return

    try:
        prefix = clean_line[0]
        val_str = clean_line[1:].strip()
        cap_val = float(val_str)
        if prefix == 'S':
            with open(CSV_FILENAME, 'a') as f:
                f.write(f"{cap_val},nF\n")
            print(f"\rLive Data [SAVED] -> {cap_val:7.3f} nF        ", end='', flush=True)
        elif prefix == 'U':
            print(f"\rLive Data -> {cap_val:7.3f} \u03bcF        ", end='', flush=True)
        elif prefix == 'N':
            print(f"\rLive Data -> {cap_val:7.3f} nF        ", end='', flush=True)
    except: pass

def notification_handler(sender, data):
    global data_buffer
    data_buffer += data.decode('utf-8', errors='ignore')
    if "\n" in data_buffer:
        lines = data_buffer.split("\n")
        for line in lines[:-1]:
            process_complete_line(line)
        data_buffer = lines[-1]

async def run_bluetooth_logger():
    print(f"Attempting to connect to {address}...")
    async with BleakClient(address, timeout=20.0) as client:
        while True:
            print("Searching for UART characteristic...")
            char = client.services.get_characteristic(UART_RX_CHAR_UUID)
            if char:
                break
            print("Characteristic not found yet. STM32 might be idle. Retrying in 5s...")
            await asyncio.sleep(5)
            await client.get_services() # Force refresh services

        print(f"Connected! Monitoring {UART_RX_CHAR_UUID}. Waiting for STM32 data...")
        await client.start_notify(UART_RX_CHAR_UUID, notification_handler)
        
        while client.is_connected:
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(run_bluetooth_logger())
        else:
            asyncio.run(run_bluetooth_logger())
    except KeyboardInterrupt:
        print("\n--- Session Ended by User ---")