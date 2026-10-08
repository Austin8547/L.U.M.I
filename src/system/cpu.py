import psutil


def cpu_load_check():

    print("=== CPU Usage ===")

    # Overall CPU usage
    avg_cpu = psutil.cpu_percent(interval=3)
    print(f"Average CPU Load: {avg_cpu}%")

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

    print("\n=== Top CPU Processes ===")
    print(f"{'PID':<8} {'Process':<30} {'CPU %':<10}")
    print("-" * 50)

    for process in top_processes:
        print(
            f"{process['pid']:<8} "
            f"{process['name']:<30} "
            f"{process['cpu']:.1f}%"
        )


def main():
    cpu_load_check()


