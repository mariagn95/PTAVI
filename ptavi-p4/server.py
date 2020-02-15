#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import json
import socketserver
from datetime import datetime, date, time, timedelta

if len(sys.argv) != 2:
    sys.exit('Usage: python3 server.py <port>')


class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    dicc = {}

    def handle(self):
        self.json2register()
        mess = []
        for line in self.rfile:
            if line.decode('utf-8') != '\r\n':
                mess.append(line.decode('utf-8'))
        user = mess[0].split()[1].split(':')[1]
        if mess[0].split()[0] == 'REGISTER':
            expires = int(mess[1].split()[1])
            user_dicc = {}
            if expires != 0:
                exp_time = datetime.now() + timedelta(seconds=int(expires))
                user_dicc['address'] = self.client_address[0]
                user_dicc['expires'] = exp_time.strftime('%H:%M:%S %d-%m-%Y')
                self.dicc[user] = user_dicc
                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
            else:
                try:
                    del self.dicc[user]
                    self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                except:
                    pass
        self.expires_users()
        self.register2json()

    def expires_users(self):
        now = datetime.now().strftime('%H:%M:%S %d-%m-%Y')
        user_del = []
        for user in self.dicc:
            if now >= self.dicc[user]['expires']:
                user_del.append(user)
        for user in user_del:
            del self.dicc[user]

    def register2json(self):
        with open('registered.json', 'w') as jsonfile:
            json.dump(self.dicc, jsonfile, indent=3)

    def json2register(self):
        try:
            with open('registered.json', 'r') as jsonfile:
                self.dicc = json.load(jsonfile)
        except:
            pass

if __name__ == "__main__":
    serv = socketserver.UDPServer(('', int(sys.argv[1])), SIPRegisterHandler)

    print("Register SIP server")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("End server")
