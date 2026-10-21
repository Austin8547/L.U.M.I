import psutil
import GPUtil

from pynvml import (
    nvmlInit,
    nvmlDeviceGetHandleByIndex,
    nvmlDeviceGetCount,
    nvmlDeviceGetComputeRunningProcesses,
    nvmlDeviceGetGraphicsRunningProcesses,
    nvmlShutdown
)


def gpu_resource_check():

    result = []

    # -------------------------
    # GPU Resource Information
    # -------------------------

    gpus = GPUtil.getGPUs()

    if not gpus:
        result.append("No GPU detected.")

    for gpu in gpus:
        result.append(
            f"GPU ID: {gpu.id} | Name: {gpu.name}"
        )

        result.append(
            f"  GPU Load:   {gpu.load * 100:.1f}%"
        )

        result.append(
            f"  VRAM Used:  {gpu.memoryUsed:.0f} MB / "
            f"{gpu.memoryTotal:.0f} MB"
        )

    # -------------------------
    # GPU Process VRAM Usage
    # -------------------------

    nvmlInit()

    try:
        device_count = nvmlDeviceGetCount()

        for gpu_id in range(device_count):

            handle = nvmlDeviceGetHandleByIndex(gpu_id)

            result.append(
                f"\n--- GPU {gpu_id} Process VRAM Usage ---"
            )

            # Collect compute processes
            processes = []

            try:
                processes.extend(
                    nvmlDeviceGetComputeRunningProcesses(handle)
                )
            except Exception:
                pass

            # Collect graphics processes
            try:
                processes.extend(
                    nvmlDeviceGetGraphicsRunningProcesses(handle)
                )
            except Exception:
                pass

            if not processes:
                result.append(
                    "  No active processes utilizing VRAM."
                )
                continue

            result.append(
                f"{'PID':<8} "
                f"{'Process Name':<30} "
                f"{'VRAM Used (MB)':<15}"
            )

            result.append("-" * 55)

            seen_pids = set()

            for proc in processes:

                pid = proc.pid

                if pid in seen_pids:
                    continue

                seen_pids.add(pid)

                # Convert bytes to MB
                vram_mb = (
                    proc.usedGpuMemory / (1024 ** 2)
                    if proc.usedGpuMemory is not None
                    else 0
                )

                # Get process name
                try:
                    name = psutil.Process(pid).name()

                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied
                ):
                    name = "[Unknown / Terminated]"

                result.append(
                    f"{pid:<8} "
                    f"{name:<30} "
                    f"{vram_mb:<15.2f}"
                )

    finally:
        # Always shut down NVML
        nvmlShutdown()

    # Return everything to the agent
    return "\n".join(result)