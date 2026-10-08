import psutil
import GPUtil

gpus = GPUtil.getGPUs()
for gpu in gpus:
    print(f"GPU ID: {gpu.id} | Name: {gpu.name}")
    print(f"  GPU Load:   {gpu.load * 100:.1f}%")
    print(f"  VRAM Used:  {gpu.memoryUsed:.0f} MB / {gpu.memoryTotal:.0f} MB")


def gpu_resource_check():
    
    gpus = GPUtil.getGPUs()
    for gpu in gpus:
        print(f"GPU ID: {gpu.id} | Name: {gpu.name}")
        print(f"  GPU Load:   {gpu.load * 100:.1f}%")
        print(f"  VRAM Used:  {gpu.memoryUsed:.0f} MB / {gpu.memoryTotal:.0f} MB")
        
    from pynvml import (
    nvmlInit,
    nvmlDeviceGetHandleByIndex,
    nvmlDeviceGetCount,
    nvmlDeviceGetComputeRunningProcesses,
    nvmlDeviceGetGraphicsRunningProcesses,
    nvmlShutdown
    )
    
    import psutil

# Initialize NVML
    nvmlInit()

    device_count = nvmlDeviceGetCount()

    for gpu_id in range(device_count):
        handle = nvmlDeviceGetHandleByIndex(gpu_id)
        print(f"\n--- GPU {gpu_id} Process VRAM Usage ---")
    
    # Collect both compute (CUDA/AI) and graphics (display/render) processes
        processes = []
        try:
            processes.extend(nvmlDeviceGetComputeRunningProcesses(handle))
        except Exception:
            pass

        try:
            processes.extend(nvmlDeviceGetGraphicsRunningProcesses(handle))
        except Exception:
            pass

        if not processes:
            print("  No active processes utilizing VRAM.")
            continue

        print(f"{'PID':<8} {'Process Name':<30} {'VRAM Used (MB)':<15}")
        print("-" * 55)

        seen_pids = set()
        for proc in processes:
            pid = proc.pid
            if pid in seen_pids:
                continue
            seen_pids.add(pid)

            # Convert bytes to Megabytes (MB)
            vram_mb = proc.usedGpuMemory / (1024 ** 2) if proc.usedGpuMemory is not None else 0

            # Retrieve human-readable process name via psutil
            try:
                name = psutil.Process(pid).name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                name = "[Unknown / Terminated]"

            print(f"{pid:<8} {name:<30} {vram_mb:<15.2f}")

    # Shutdown NVML session
    nvmlShutdown()
    


