#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import sys
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from proxy_registrar import XMLHandler, digest_response, log
from uaserver import TAGS

METHODS_ALLOWED = ['REGISTER', 'INVITE', 'BYE']


class SIPMessages:

    def __init__(self, xmlfile):
        parser = make_parser()
        xml = XMLHandler(TAGS)
        parser.setContentHandler(xml)
        parser.parse(open(xmlfile))
        self.config = xml.get_tags()

    def register(self, option, digest=''):
        mess = 'REGISTER sip:' + self.config['account_username'] + ':'
        mess += self.config['uaserver_puerto'] + ' SIP/2.0\r\nExpires: '
        mess += str(option)
        if digest != '':
            mess += '\r\nAuthorization: Digest response="' + digest + '"'

        return mess + '\r\n'

    def ack(self, option):
        mess = 'ACK sip:' + option + ' SIP/2.0\r\n'

        return mess + '\r\n'

    def invite(self, option):
        username = self.config['account_username']
        ip = self.config['uaserver_ip']
        rtpport = self.config['rtpaudio_puerto']
        mess = 'INVITE sip:' + option + ' SIP/2.0\r\nContent-Type:'
        mess += ' application/sdp\r\n\r\nv=0\r\no=' + username + ' ' + ip
        mess += '\r\ns=sesionguay\r\nt=0\r\nm=audio ' + rtpport + ' RTP'

        return mess + '\r\n'

    def bye(self, option):
        mess = 'BYE sip:' + option + ' SIP/2.0\r\n'

        return mess + '\r\n'


def get_message(sip_mess, method, opt1, opt2=''):  # opts = [opt1,opt2,...]
    if method.lower() == 'register':
        return sip_mess.register(opt1, opt2)
    elif method.lower() == 'invite':
        return sip_mess.invite(opt1)
    elif method.lower() == 'bye':
        return sip_mess.bye(opt1)
    elif method.lower() == 'ack':
        return sip_mess.ack(opt1)


def invite_response(data):
    ok_100 = '100' in data
    ok_180 = '180' in data
    ok_200 = '200' in data
    return ok_100 and ok_180 and ok_200

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit('Usage: python3 uaclient.py config metodo opcion')
    else:
        xmlfile = sys.argv[1]
        method = sys.argv[2]
        option = sys.argv[3]
    sip = SIPMessages(xmlfile)
    proxy_ip = sip.config['regproxy_ip']
    proxy_port = int(sip.config['regproxy_puerto'])
    log('Starting...', sip.config)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        mess = get_message(sip, method, option)
        my_socket.connect((proxy_ip, proxy_port))
        log_mess = 'Sent to ' + proxy_ip + ':'
        log_mess += str(proxy_port) + ': '
        log_mess += mess.replace('\r\n', ' ')
        log(log_mess, sip.config)
        my_socket.send(bytes(mess, 'utf-8') + b'\r\n')
        try:
            data = my_socket.recv(1024).decode('utf-8')
            if data:
                log_mess = 'Received from ' + proxy_ip + ':'
                log_mess += str(proxy_port) + ': '
                log_mess += data.replace('\r\n', ' ')
                log(log_mess, sip.config)
        except:
            data = ''
            error = 'Error: No server listening at ' + proxy_ip
            error += ' port ' + str(proxy_port)
            log(error, sip.config)
        print(data)
        if 'Authenticate' in data and method.lower() == 'register':
            nonce = data.split('"')[1]
            dig = digest_response(nonce, sip.config['account_passwd'])
            mess = get_message(sip, method, option, dig)
            log_mess = 'Sent to ' + proxy_ip + ':'
            log_mess += str(proxy_port) + ': '
            log_mess += mess.replace('\r\n', ' ')
            log(log_mess, sip.config)
            my_socket.send(bytes(mess, 'utf-8') + b'\r\n')
            try:
                data = my_socket.recv(1024).decode('utf-8')
                log_mess = 'Received from ' + proxy_ip + ':'
                log_mess += str(proxy_port) + ': '
                log_mess += data.replace('\r\n', ' ')
                log(log_mess, sip.config)
            except:
                data = ''
                error = 'Error: No server listening at ' + proxy_ip
                error += ' port ' + str(proxy_port)
                log(error, sip.config)
            print(data)
        elif invite_response(data):
            ip = data.split('\r\n')[8].split()[1]
            port = data.split('\r\n')[11].split()[1]
            audio = sip.config['audio_path']
            mp32rtp = './mp32rtp -i ' + ip + ' -p ' + port + ' < ' + audio
            ack = get_message(sip, 'ack', option)
            log_mess = 'Sent to ' + proxy_ip + ':'
            log_mess += str(proxy_port) + ': '
            log_mess += mess.replace('\r\n', ' ')
            log(log_mess, sip.config)
            my_socket.send(bytes(ack, 'utf-8') + b'\r\n')
            print('Running audio...')
            os.system(mp32rtp)
            print('End audio')
        elif data == '':
            print("Error: No server listening.")
            error = 'Error: No server listening at ' + proxy_ip
            error += ' port ' + str(proxy_port)
            log(error, sip.config)
    log('Finishing.', sip.config)
