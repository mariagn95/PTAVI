#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import sys
import json
import socketserver
import hashlib
from datetime import datetime, date, time, timedelta
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

TAGS = {"server": ['name', 'ip', 'puerto'],
        "database": ['path', 'passwdpath'],
        "log": ['path']}


def digest_response(nonce, passwd):
    dig = hashlib.sha224()
    dig.update(bytes(nonce + passwd, 'utf-8'))
    return dig.hexdigest()


def digest_nonce(username, servername):
    dig = hashlib.sha224()
    dig.update(bytes(username + servername, 'utf-8'))
    return dig.hexdigest()


def log(mess, config):
    with open(config['log_path'], 'a') as log_file:
        now = datetime.now().strftime('%Y%m%d%H%M%S')
        log_msg = now + ' ' + mess + '\n'
        log_file.write(log_msg)


class XMLHandler(ContentHandler):

    def __init__(self, tags):
        self.tags = tags
        self.list = {}

    def startElement(self, name, attrs):
        if name in self.tags:
            for att in self.tags[name]:
                self.list[name + '_' + att] = attrs.get(att, '')

    def get_tags(self):
        return self.list


class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    dicc = {}
    passwd = {}
    methods_allowed = ['REGISTER', 'INVITE', 'BYE', 'ACK']

    def handle(self):
        mess = ''
        self.json2passwd()
        self.json2register()
        mess = self.rfile.read().decode('utf-8')
        log_mess = 'Received from ' + self.client_address[0] + ':'
        log_mess += str(self.client_address[1]) + ': '
        log_mess += mess.replace('\r\n', ' ')
        log(log_mess, config)
        print(mess)
        if 'SIP/2.0' in mess:
            method = mess.split()[0]
            if method in self.methods_allowed:
                print(method, 'receive')
                if method.lower() == 'register':
                    username = mess.split(':')[1]
                    if username in self.dicc:
                        exp = mess.split(':')[-1]
                        if int(exp) == 0:
                            del self.dicc[username]
                        else:
                            t = datetime.now() + timedelta(seconds=int(exp))
                            expires = t.strftime('%H:%M:%S %d-%m-%Y')
                            self.dicc[username]['expires'] = expires
                        self.wfile.write(b'SIP/2.0 200 OK\r\n')
                        log_mess = 'Sent to ' + self.client_address[0] + ':'
                        log_mess += str(self.client_address[1]) + ': '
                        log_mess += ': SIP/2.0 200 OK'
                        log(log_mess, config)
                    else:
                        if 'Digest response' in mess:
                            server_name = config['server_name']
                            nonce = digest_nonce(username, server_name)
                            user_resp = mess.split('"')[1]
                            passwd = self.passwd[username]
                            resp = digest_response(nonce, passwd)
                            if resp == user_resp:
                                port = mess.split()[1].split(':')[2]
                                s = mess.split(':')[3].split()[0]
                                t = datetime.now() + timedelta(seconds=int(s))
                                exp = t.strftime('%H:%M:%S %d-%m-%Y')
                                ip = self.client_address[0]
                                self.dicc[username] = {'ip': ip,
                                                       'port': port,
                                                       'expires': exp}
                                response = 'SIP/2.0 200 OK\r\n'
                                self.wfile.write(bytes(response, 'utf-8'))
                                log_mess = 'Sent to ' + self.client_address[0]
                                log_mess += ':' + str(self.client_address[1])
                                log_mess += ': SIP/2.0 200 OK'
                                log(log_mess, config)
                                print(response)
                            else:
                                # 404 User not Found
                                response = 'SIP/2.0 404 User not Found\r\n'
                                self.wfile.write(bytes(response, 'utf-8'))
                                print(response)
                        else:
                            # 401 Unathorized
                            server_name = config['server_name']
                            nonce = digest_nonce(username, server_name)
                            response = 'SIP/2.0 401 Unathorized\r\n'
                            response += 'WWW Authenticate: Digest nonce="'
                            response += nonce + '"\r\n'
                            self.wfile.write(bytes(response, 'utf-8'))
                            log_mess = 'Sent to ' + self.client_address[0]
                            log_mess += ':' + str(self.client_address[1])
                            log_mess += ': ' + response.replace('\r\n', ' ')
                            log(log_mess, config)
                            print(response)
                else:
                    user_dst = mess.split(':')[1].split()[0]
                    if method.lower() == 'invite':
                        user_src = mess.split('\n')[4].split('=')[1].split()[0]
                        if user_src in self.dicc and user_dst in self.dicc:
                            data = self.sent_to(user_dst, mess)
                            self.wfile.write(bytes(data, 'utf-8'))
                            log_mess = 'Sent to ' + self.client_address[0]
                            log_mess += ':' + str(self.client_address[1])
                            log_mess += ': ' + data.replace('\r\n', ' ')
                            log(log_mess, config)
                        else:
                            response = 'SIP/2.0 404 User not Found\r\n'
                            self.wfile.write(bytes(response, 'utf-8'))
                            log_mess = 'Sent to ' + self.client_address[0]
                            log_mess += ':' + str(self.client_address[1])
                            log_mess += ': ' + response.replace('\r\n', ' ')
                            log(log_mess, config)
                            print(response)
                    else:
                        data = self.sent_to(user_dst, mess)
                        self.wfile.write(bytes(data, 'utf-8'))
                        log_mess = 'Sent to ' + self.client_address[0]
                        log_mess += ':' + str(self.client_address[1])
                        log_mess += ': ' + data.replace('\r\n', ' ')
                        log(log_mess, config)
            else:
                response = 'SIP/2.0 405 Method Not Allowed\r\n'
                self.wfile.write(bytes(response, 'utf-8'))
                log_mess = 'Sent to ' + self.client_address[0]
                log_mess += ':' + str(self.client_address[1])
                log_mess += ': ' + response.replace('\r\n', ' ')
                log(log_mess, config)
                print(response)
        else:
            # 400 Bad Request
            response = 'SIP/2.0 400 Bad Request\r\n'
            self.wfile.write(bytes(response, 'utf-8'))
            log_mess = 'Sent to ' + self.client_address[0]
            log_mess += ':' + str(self.client_address[1])
            log_mess += ': ' + response.replace('\r\n', ' ')
            log(log_mess, config)
            print(response)

        self.expires_users()
        self.register2json()

    def sent_to(self, userdest, mess):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
                ip = self.dicc[userdest]['ip']
                port = int(self.dicc[userdest]['port'])
                my_socket.connect((ip, port))
                log_mess = 'Sent to ' + ip + ':'
                log_mess += str(port) + ': '
                log_mess += mess.replace('\r\n', ' ')
                log(log_mess, config)
                my_socket.send(bytes(mess, 'utf-8') + b'\r\n')
                data = my_socket.recv(1024).decode('utf-8')
        except:
            data = ''

        return data

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

    def json2passwd(self):
        try:
            with open('passwords.json', 'r') as jsonfile:
                self.passwd = json.load(jsonfile)
        except:
            pass

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit('Usage: python3 proxy_registrar.py config')
    else:
        xmlfile = sys.argv[1]
    parser = make_parser()
    cHandler = XMLHandler(TAGS)
    parser.setContentHandler(cHandler)
    parser.parse(open(xmlfile))
    config = cHandler.get_tags()

    ip = config['server_ip']
    port = int(config['server_puerto'])
    serv = socketserver.UDPServer((ip, port), SIPRegisterHandler)
    print(config['server_name'])
    try:
        log('Starting...', config)
        serv.serve_forever()
    except KeyboardInterrupt:
        print("End server")
        log('Finishing.', config)
