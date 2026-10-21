from langchain_core.tools import tool

from src.system.cpu import cpu_load_check
from src.system.ram import ram_usage_check
from src.system.gpu import gpu_resource_check
from src.system.temperature import system_temp_check
from src.system.power import system_power_check

@tool
def get_cpu_status():
    """Get current CPU usage and top CPU-consuming processes."""
    return cpu_load_check()


@tool
def get_ram_status():
    """Get current RAM usage and top RAM-consuming processes."""
    return ram_usage_check()


@tool
def get_gpu_status():
    """Get GPU utilization, VRAM usage, and GPU processes."""
    return gpu_resource_check()


@tool
def get_temperature_status():
    """Get CPU/system and NVIDIA GPU temperatures."""
    return system_temp_check()


@tool
def get_battery_status():
    """Get the battery status of tje system"""
    return system_power_check()




    