from src.system.cpu import cpu_load_check
from src.system.ram import ram_usage_check
from src.system.gpu import gpu_resource_check
from src.system.temperature import system_temp_check
from src.system.power import system_power_check

def get_system_status():
    cpu_load_check()
    ram_usage_check()
    gpu_resource_check()
    system_temp_check()
    system_power_check()
    
    
get_system_status()