#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.append("../")
from extractor import Extractor
import chardet
import time

class TimeInterval(Extractor):
    def __init__(self):
        Extractor.__init__(self)

    def get_feature_num(self):
        return 1

    def extract_all(self, nodes):
        features = list()
        pair_idx = -1
        timestamp = []
        for nd in nodes:
            if pair_idx != -1 and int(nd[0]) != pair_idx:
                features.append(43200)
                features += [timestamp[i + 1] - timestamp[i] for i in range(len(timestamp) - 1)]
                timestamp = []
            pair_idx = int(nd[0])
            # timestamp.append(time.mktime(time.strptime(info_list[1], "%Y-%m-%d %H:%M:%S")))
            timestamp.append(time.mktime(time.strptime(nd[1], "%Y/%m/%d %H:%M")))
        features.append(43200)
        features += [timestamp[i + 1] - timestamp[i] for i in range(len(timestamp) - 1)]
        print features
        return features

if __name__ == '__main__':
    TimeInterval().extract()