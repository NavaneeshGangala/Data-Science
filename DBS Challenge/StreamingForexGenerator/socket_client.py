#!/usr/bin/python3

import socket
import time
import sys

HOST='localhost'
PORT=7047

# 1 seconds of sleep
SLEEP_TIME = 1/6

if __name__ == "__main__":

    if len(sys.argv) == 2:
        port_number = int(sys.argv[1])
    else:
        port_number = PORT

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, port_number))

    while True:

        data = sock.recv(2000)
        print(data.decode())
        time.sleep(SLEEP_TIME)


