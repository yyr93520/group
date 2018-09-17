#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.append("../")
from extractor import Extractor
import chardet
import time

class SMSLength(Extractor):
    def __init__(self):
        Extractor.__init__(self)

    def get_feature_num(self):
        return 1

    def extract_all(self, nodes):
        features = list()
        for nd in nodes:
            features.append(len(nd[4].decode('utf-8')))
        print features
        return features

if __name__ == '__main__':
    SMSLength().extract()