#!/usr/bin/python3
# -*- coding: utf-8 -*-


import socketserver
import sys
import os

if len(sys.argv) != 4:
    sys.exit('Usage: python3 server.py IP port audio_file')
else:
    IP = sys.argv[1]
    port = int(sys.argv[2])
    audio_file = sys.argv[3]

Trying = b'SIP/2.0 100 Trying\r\n'
Ringing = b'SIP/2.0 180 Ringing\r\n'
OK = b'SIP/2.0 200 OK\r\n'
Bad_Request = b'SIP/2.0 400 Bad Request\r\n'
Method_Not_Allowed = b'SIP/2.0 405 Method Not Allowed\r\n'


class EchoHandler(socketserver.DatagramRequestHandler):

    def check_request(self, mess):
        try:
            request_sip = ("sip" in mess[1].split(":")[0])
            request_arr = False  # request_arr = @
            request_end = ("SIP/2.0" in mess[2])
            if '@' in str(mess[1]):
                request_arr = True
            if request_sip and request_arr and request_end:
                return True
            else:
                return False
        except TypeError:
            return False

    def handle(self):
        mess = self.rfile.read().decode('utf-8')
        Method = mess.split()[0]
        if Method in mess.split()[0] and self.check_request(mess.split()):
            if Method == 'INVITE':
                print("--The client sends " + mess)
                self.wfile.write(Trying + Ringing + OK + b'\r\n')
            elif Method == 'ACK':
                print("--The client sends " + mess)
                aEjecutar = 'mp32rtp -i 127.0.0.1 -p 23032 < ' + audio_file
                os.system(aEjecutar)
            elif Method == 'BYE':
                print("--The client sends " + mess)
                self.wfile.write(OK + b'\r\n')
            else:
                self.wfile.write(Method_Not_Allowed + b'\r\n')

        else:
            self.wfile.write(Bad_Request + b'\r\n')


if __name__ == "__main__":

    serv = socketserver.UDPServer((IP, port), EchoHandler)
    print("Listenig...")

    try:
        serv.serve_forever()

    except KeyboardInterrupt:
        print("End Server.")
