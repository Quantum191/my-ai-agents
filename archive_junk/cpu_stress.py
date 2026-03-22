#!/usr/bin/env python3
import time

def is_prime(num):
    if num <= 1:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True

def calculate_primes_for_time(duration):
    start_time = time.time()
    while (time.time() - start_time) < duration:
        for number in range(2, 100000):  # Adjust the range for more or less CPU stress
            if is_prime(number):
                pass

if __name__ == '__main__':
    calculate_primes_for_time(15)