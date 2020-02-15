#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import socket

if len(sys.argv) != 6:
    sys.exit('Usage: python3 client.py <ip> <port> <method> <user> <expires>')
else:
    mess = str.upper(sys.argv[3]) + ' sip:' + sys.argv[4] + ' SIP/2.0\r\n'
    mess += 'Expires: ' + sys.argv[5] + '\r\n'

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
    my_socket.connect((sys.argv[1], int(sys.argv[2])))
    my_socket.send(bytes(mess, 'utf-8') + b'\r\n')
    data = my_socket.recv(1024)
    print('Receive -- ', data.decode('utf-8'))

print("End socket.")
