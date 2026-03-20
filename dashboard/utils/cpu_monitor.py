import psutil

def get_cpu_stats():
    try:
        # Getting usage
        usage = psutil.cpu_percent(interval=None)
        
        # Getting temperature (looking for k10temp on AMD or coretemp on Intel)
        temp = 0
        temps = psutil.sensors_temperatures()
        for name in ['k10temp', 'coretemp', 'cpu_thermal']:
            if name in temps:
                temp = temps[name][0].current
                break
        
        return usage, temp
    except Exception:
        return 0.0, 0.0
