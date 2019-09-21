#!/usr/bin/python3

import socket
import random
import time
import sys
import json

# 1/6 seconds of sleep
SLEEP_TIME = 1/6
PORT_NUMBER = 7047
VARIANCE_VAL = 0.006


class ForexGenerator:
    def __init__(self):

        self._last_response = None
        self._feed_file_name = "seed_rates.json"

        with open(self._feed_file_name, 'r') as f:
            self._last_response = json.load(f)

    def get_next_rate(self):

        new_response = {}
        new_response["timestamp"] = str(time.time() * 100000)
        new_response["rates"] = []
        last_rates = self._last_response.get("rates")
        for item in last_rates:
            new_rate = {}
            new_rate["currency"] = item["currency"]
            current_rate = item["rate"]
            fluctuation_value = VARIANCE_VAL * current_rate
            new_rate_value = current_rate + random.uniform(-fluctuation_value, fluctuation_value)
            new_rate["rate"] = new_rate_value
            new_response["rates"].append(new_rate)

        self._last_response = new_response
        return json.dumps(new_response)


if __name__=="__main__":
    HOST = ''

    if len(sys.argv) == 2:
        port_number = int(sys.argv[1])
    else:
        port_number = PORT_NUMBER

    PORT = int(port_number)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(1)
    conn, addr = sock.accept()

    print('Connected by ', addr)
    conn.sendall("Welcome to the Forex server!".encode())

    forex_generator = ForexGenerator()

    while True:
        # data = conn.recv(1024)
        val = forex_generator.get_next_rate()
        print(val)
        # if not data: break
        conn.sendall(val.encode())
        time.sleep(SLEEP_TIME)

    # conn.close()