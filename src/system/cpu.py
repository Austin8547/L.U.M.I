import psutil


def cpu_load_check():

    # Overall CPU usage
    avg_cpu = psutil.cpu_percent(interval=3)

    # Get CPU usage of processes
    processes = []

    for process in psutil.process_iter(["pid", "name", "cpu_percent"]):
        try:
            cpu = process.info["cpu_percent"]

            processes.append({
                "pid": process.info["pid"],
                "name": process.info["name"],
                "cpu": cpu
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # Sort by CPU usage
    top_processes = sorted(
        processes,
        key=lambda x: x["cpu"],
        reverse=True
    )[:5]

    # Build result for the agent
    result = []

    result.append("=== CPU Usage ===")
    result.append(f"Average CPU Load: {avg_cpu}%")

    result.append("\n=== Top CPU Processes ===")
    result.append(f"{'PID':<8} {'Process':<30} {'CPU %':<10}")
    result.append("-" * 50)

    for process in top_processes:
        result.append(
            f"{process['pid']:<8} "
            f"{process['name']:<30} "
            f"{process['cpu']:.1f}%"
        )

    return "\n".join(result)


