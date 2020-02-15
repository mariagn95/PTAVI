#!/usr/bin/python3
# -*- coding: utf-8 -*-

from xml.sax import make_parser
from xml.sax.handler import ContentHandler


class SmallSMILHandler(ContentHandler):

    def __init__(self):
        self.tags = {"root-layout": ["width", "height", "background-color"],
                     "region": ["id", "top", "bottom", "left", "right"],
                     "img": ["src", "region", "begin", "dur"],
                     "audio": ["src", "begin", "dur"],
                     "textstream": ["src", "region"]}
        self.list = []

    def startElement(self, name, attrs):
        Dicc = {}
        if name in self.tags:
            Dicc["elements"] = name
            for attributes in self.tags[name]:
                Dicc[attributes] = attrs.get(attributes, " ")
            self.list.append([name, Dicc])

    def get_tags(self):
        return self.list

if __name__ == "__main__":

    parser = make_parser()
    cHandler = SmallSMILHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open('karaoke.smil'))

    print(cHandler.get_tags())
