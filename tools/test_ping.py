# This is a test script for pinging a host
import os

def ping(host):
    response = os.system(f'ping -c 1 {host}')
    if response == 0:
        return True
    else:
        return False

if __name__ == '__main__':
    host = 'google.com'
    result = ping(host)
    print(f'Ping to {host} successful: {result}')