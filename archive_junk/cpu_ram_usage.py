#!/usr/bin/env python3

import psutil
import json
from datetime import datetime

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_ram_usage():
    memory = psutil.virtual_memory()
    return {
        'total': memory.total,
        'available': memory.available,
        'used': memory.used,
        'percent_used': memory.percent
    }

if __name__ == '__main__':
    data = {
        'timestamp': str(datetime.now()),
        'cpu_usage': get_cpu_usage(),
        'ram_usage': get_ram_usage()
    }
    with open('usage_data.json', 'w') as f:
        json.dump(data, f, indent=4)

print("CPU and RAM usage data saved to usage_data.json")