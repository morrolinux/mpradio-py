#!/usr/bin/env python
import signal
import os
import time

print('My PID is:', os.getpid())

def handler(signum, frame):
   time.sleep(1)
   print("handler called")
   if signum == signal.SIGUSR1:
       print('user defined interrupt!')

signal.signal(signal.SIGUSR1, handler)

while True:
    print('Waiting...')
    time.sleep(3)
