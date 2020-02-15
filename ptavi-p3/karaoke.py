#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import json
import urllib.request
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from smallsmilhandler import SmallSMILHandler


class KaraokeLocal:
    def __init__(self, list):
        parser = make_parser()
        cHandler = SmallSMILHandler()
        parser.setContentHandler(cHandler)
        parser.parse(fichero)
        self.list = cHandler.get_tags()

    def __str__(self):
        tag_line = ''
        for name in self.list:
            tag_line += name[0] + "\t"
            for info in name[1]:
                if info != 'elements' and name[1][info] != " ":
                    tag_line += info + '="' + name[1][info] + '"\t'
            tag_line += '\n'
        return tag_line

    def do_json(self, file_smil, file_json=''):
        if file_json == '':
            file_json = file_smil.replace('smil', 'json')

        with open(file_json, 'w') as jsonfile:
            json.dump(self.list, jsonfile, indent=3)

    def do_local(self):
        for name in self.list:
            for info in name[1]:
                if info == 'src':
                    if name[1][info].startswith('http://'):
                        url = name[1][info]
                        file_name = url.split('/')[-1]
                        urllib.request.urlretrieve(url, file_name)
                        name[1][info] = file_name

if __name__ == "__main__":
    try:
        fichero = sys.argv[1]
    except:
        sys.exit("Error. Usage: python3 karaoke.py file.smil")
    karaoke = KaraokeLocal(fichero)
    print(karaoke)
    karaoke.do_json(fichero)
    karaoke.do_local()
    karaoke.do_json(fichero, 'local.json')
    print(karaoke)
