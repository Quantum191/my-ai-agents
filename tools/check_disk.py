import json

#!/usr/bin/env python3
import shutil

def get_disk_usage():
    total, used, free = shutil.disk_usage('/')
    return {
        'total': total,
        'used': used,
        'free': free,
        'percent_used': (used / total) * 100
    }

if __name__ == '__main__':
    disk_info = get_disk_usage()
    print(json.dumps(disk_info, indent=4))