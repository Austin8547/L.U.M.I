import psutil


def ram_usage_check():

    # Total RAM information
    ram = psutil.virtual_memory()

    total_ram = ram.total / (1024 ** 3)
    used_ram = ram.used / (1024 ** 3)
    available_ram = ram.available / (1024 ** 3)

    print("=== RAM Usage ===")
    print(f"Total RAM:     {total_ram:.2f} GB")
    print(f"Used RAM:      {used_ram:.2f} GB")
    print(f"Available RAM: {available_ram:.2f} GB")
    print(f"RAM Usage:     {ram.percent}%")

    # Get RAM usage of processes
    processes = []

    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            rss_bytes = proc.info['memory_info'].rss
            rss_mb = rss_bytes / (1024 * 1024)

            processes.append({
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'memory_mb': rss_mb
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # Top 5 RAM-consuming processes
    top5 = sorted(
        processes,
        key=lambda p: p['memory_mb'],
        reverse=True
    )[:5]

    print("\n=== Top RAM Processes ===")
    print(f"{'PID':<8} {'Process Name':<30} {'RAM Usage (MB)':<15}")
    print("-" * 55)

    for proc in top5:
        print(
            f"{proc['pid']:<8} "
            f"{proc['name']:<30} "
            f"{proc['memory_mb']:.2f} MB"
        )

