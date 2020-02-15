#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import sys


if len(sys.argv) != 3:
    sys.exit('Usage: python3 client.py method receiver@IP:SIPport')
else:
    Method = sys.argv[1]  # INVITE, BYE
    User = sys.argv[2].split("@")[0]
    IP = sys.argv[2].split("@")[1].split(":")[0]
    SIPport = int(sys.argv[2].split("@")[1].split(":")[1])

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((IP, SIPport))

    try:
        print(Method + ' sip:' + User + "@" + IP + ' SIP/2.0')
        my_socket.send(bytes(Method + ' sip:' + User + "@"
                             + IP + ' SIP/2.0', 'utf-8') + b'\r\n\r\n')
        data = my_socket.recv(1024)
        print("Sending: " + Method)
        mess = data.decode('utf-8').split()
        if mess[1] == "100" and mess[4] == "180" and mess[7] == "200":
            print('Received -- ', data.decode('utf-8').replace('\r\n', ' '))
            my_socket.send(bytes("ACK" + " sip:" + User + "@"
                                 + IP + " SIP/2.0", 'utf-8') + b'\r\n\r\n')
            print("Send ACK")
        else:
            print('Received -- ', data.decode('utf-8').replace('\r\n', ' '))
            print("Finishing socket...")
    except ConnectionRefusedError:
        print("Conection refused")

print("End client.")
