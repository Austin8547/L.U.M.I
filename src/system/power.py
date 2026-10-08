
import psutil

def system_power_check():
    
    battery = psutil.sensors_battery()

    if battery is None:
        print("No battery detected on this system (Desktop / AC-only device).")
    else:
        percent = battery.percent
        plugged = battery.power_plugged
        secs_left = battery.secsleft

        print(f"Battery Charge: {percent}%")
        print(f"Power Plugged In: {'Yes' if plugged else 'No'}")

        # Process remaining time estimation
        if secs_left == psutil.POWER_TIME_UNLIMITED:
            print("Estimated Time Remaining: Unlimited (Charging / Fully Charged)")
        elif secs_left == psutil.POWER_TIME_UNKNOWN:
            print("Estimated Time Remaining: Calculating...")
        else:
        # Convert seconds to Hours and Minutes
            hours = secs_left // 3600
            minutes = (secs_left % 3600) // 60
            print(f"Estimated Time Remaining: {hours}h {minutes}m")
            
            
