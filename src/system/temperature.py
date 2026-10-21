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

    result = []

    result.append("=== System Temperatures ===")

    # CPU / System temperatures
    temperatures = psutil.sensors_temperatures()

    if temperatures:
        for sensor, entries in temperatures.items():
            for entry in entries:
                name = entry.label or sensor
                result.append(f"{name}: {entry.current:.1f}°C")
    else:
        result.append("No system temperature sensors detected.")

    # NVIDIA GPU temperatures
    result.append("\n=== GPU Temperatures ===")

    nvmlInit()

    try:
        device_count = nvmlDeviceGetCount()

        if device_count == 0:
            result.append("No NVIDIA GPU detected.")

        for i in range(device_count):
            handle = nvmlDeviceGetHandleByIndex(i)

            temperature = nvmlDeviceGetTemperature(
                handle,
                NVML_TEMPERATURE_GPU
            )

            result.append(f"GPU {i}: {temperature}°C")

    finally:
        nvmlShutdown()

    return "\n".join(result)