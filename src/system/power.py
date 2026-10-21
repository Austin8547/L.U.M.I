import psutil


def system_power_check():

    battery = psutil.sensors_battery()

    if battery is None:
        return "No battery detected on this system (Desktop / AC-only device)."

    percent = battery.percent
    plugged = battery.power_plugged
    secs_left = battery.secsleft

    result = []

    result.append(f"Battery Charge: {percent}%")
    result.append(
        f"Power Plugged In: {'Yes' if plugged else 'No'}"
    )

    # Process remaining time estimation
    if secs_left == psutil.POWER_TIME_UNLIMITED:

        result.append(
            "Estimated Time Remaining: Unlimited (Charging / Fully Charged)"
        )

    elif secs_left == psutil.POWER_TIME_UNKNOWN:

        result.append(
            "Estimated Time Remaining: Calculating..."
        )

    else:

        # Convert seconds to Hours and Minutes
        hours = secs_left // 3600
        minutes = (secs_left % 3600) // 60

        result.append(
            f"Estimated Time Remaining: {hours}h {minutes}m"
        )

    return "\n".join(result)