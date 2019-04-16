#!/usr/bin/env python3

import bluetooth
import sys

if len(sys.argv) < 3:
    print("syntax:")
    print("<bt:ma:ca:dd:re:ss> <command>")
    exit(1)

bd_addr = sys.argv[1]
port = 1

sock=bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((bd_addr, port))
sock.send(sys.argv[2])
sock.close()

