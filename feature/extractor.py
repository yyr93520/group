#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.append("../")
import os
from feature import Feature
import json
from util.PropertiesUtil import PropertiesUtil

class Extractor(object):

    def __init__(self):
        self.feature_name = self.__class__.__name__

    def get_feature_num(self):
        assert False, 'Please override function: Extractor.get_feature_num()'

    def extract_all(self, nodes):
        assert False, 'Please override function: Extractor.extract_all()'

    def extract(self):
        sms_red_fp = PropertiesUtil.getProperty('PATH', 'sms_red_fp')
        sms_info = []
        for line in open(sms_red_fp, 'r'):
            sms_info.append(line.strip().split('\t'))
        feature_pt = PropertiesUtil.getProperty('PATH', 'feature_pt')
        if not os.path.exists(feature_pt):
            os.makedirs(feature_pt)
        feature_fp = '%s/%s.txt' % (feature_pt, self.feature_name)
        feature_file = open(feature_fp, 'w')
        feature_file.write('%d %d\n' % (len(sms_info), int(self.get_feature_num())))
        feature = self.extract_all(sms_info)
        Feature.save_feature(feature, feature_file)
        feature_file.close()