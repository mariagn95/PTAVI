#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import sys
import os
import socketserver
from datetime import datetime, date, time, timedelta
from xml.sax import make_parser
from proxy_registrar import XMLHandler, log

TAGS = {"account": ['username', 'passwd'],
        "uaserver": ['ip', 'puerto'],
        "rtpaudio": ['puerto'],
        "regproxy": ['ip', 'puerto'],
        "log": ['path'],
        "audio": ['path']}


class SIPHandler(socketserver.DatagramRequestHandler):

    mp32rtp = []

    def handle(self):
        mess = ''
        mess = self.rfile.read().decode('utf-8')
        log_mess = 'Received from ' + self.client_address[0] + ':'
        log_mess += str(self.client_address[1]) + ': '
        log_mess += mess.replace('\r\n', ' ')
        log(log_mess, config)
        if 'INVITE' in mess:
            # 100 trying 180 ringing 200 ok
            ip = mess.split('\r\n')[4].split()[1]
            port = mess.split('\r\n')[7].split()[1]
            self.mp32rtp.append(ip)
            self.mp32rtp.append(port)
            response = 'SIP/2.0 100 Trying\r\n\r\nSIP/2.0 180 Ringing\r\n\r\n'
            response += 'SIP/2.0 200 OK\r\nContent-Type: application/sdp\r\n'
            response += '\r\nv=0\r\no=' + config['account_username'] + ' '
            response += config['uaserver_ip'] + '\r\ns=sesionguay\r\nt=0\r\n'
            response += 'm=audio ' + config['rtpaudio_puerto'] + ' RTP\r\n'
            self.wfile.write(bytes(response, 'utf-8'))
            log_mess = 'Sent to ' + self.client_address[0] + ':'
            log_mess += str(self.client_address[1]) + ': '
            log_mess += response.replace('\r\n', ' ')
            log(log_mess, config)
        elif 'ACK' in mess:
            # reproduce cancion
            mp32rtp = './mp32rtp -i ' + self.mp32rtp[0] + ' -p '
            mp32rtp += self.mp32rtp[1] + ' < ' + config['audio_path']
            print('Running audio...')
            os.system(mp32rtp)
            print('End audio')
            self.mp32rtp = []
        elif 'BYE' in mess:
            # 200 ok
            response = 'SIP/2.0 200 OK\r\n'
            self.wfile.write(bytes(response, 'utf-8'))
            log_mess = 'Sent to ' + self.client_address[0] + ':'
            log_mess += str(self.client_address[1]) + ': '
            log_mess += mess.replace('\r\n', ' ')
            log(log_mess, config)
        else:
            # 405 method not allowed
            response = 'SIP/2.0 405 Method not Allowed\r\n'
            self.wfile.write(bytes(response, 'utf-8'))
            log_mess = 'Sent to ' + self.client_address[0] + ':'
            log_mess += str(self.client_address[1]) + ': '
            log_mess += mess.replace('\r\n', ' ')
            log(log_mess, config)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit('Usage: python3 uaserver.py config')
    else:
        xmlfile = sys.argv[1]
    parser = make_parser()
    cHandler = XMLHandler(TAGS)
    parser.setContentHandler(cHandler)
    parser.parse(open(xmlfile))
    config = cHandler.get_tags()

    address = (config['uaserver_ip'], int(config['uaserver_puerto']))
    serv = socketserver.UDPServer(address, SIPHandler)
    try:
        log('Starting...', config)
        serv.serve_forever()
    except KeyboardInterrupt:
        print("End server")
        log('Finishing.', config)
