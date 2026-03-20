import json
from tools.check_disk import get_disk_usage
def get_disk_stats():
    disk_info = get_disk_usage()
    return {
        'total': disk_info['total'],
        'used': disk_info['used'],
        'free': disk_info['free'],
        'percent_used': disk_info['percent_used']
}