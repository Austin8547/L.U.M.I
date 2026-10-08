import psutil
from pynvml import (
    nvmlInit,
    nvmlShutdown,
    nvmlDeviceGetCount,
    nvmlDeviceGetHandleByIndex,
    nvmlDeviceGetTemperature,
    NVML_TEMPERATURE_GPU,
)


def system_temp_check():

    print("=== System Temperatures ===")

    # CPU / System temperatures
    temperatures = psutil.sensors_temperatures()

    for sensor, entries in temperatures.items():
        for entry in entries:
            name = entry.label or sensor
            print(f"{name}: {entry.current:.1f}°C")

    # NVIDIA GPU temperatures
    print("\n=== GPU Temperatures ===")

    nvmlInit()

    for i in range(nvmlDeviceGetCount()):
        handle = nvmlDeviceGetHandleByIndex(i)
        temperature = nvmlDeviceGetTemperature(
            handle,
            NVML_TEMPERATURE_GPU
        )

        print(f"GPU {i}: {temperature}°C")

    nvmlShutdown()


def main():
    system_temp_check()


