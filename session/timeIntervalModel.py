#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.append("../")
import time
from util.PropertiesUtil import PropertiesUtil
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

class TimeIntervalModel(object):

    def __init__(self):
        pass

    def timeReduction(self):
        sms_red_fp = PropertiesUtil.getProperty('PATH', 'sms_red_fp')
        sms_time_fp = PropertiesUtil.getProperty('PATH', 'sms_time_fp')
        sms_tag_fp = PropertiesUtil.getProperty('PATH', 'sms_tag_fp')
        timestamp = []
        pair_idx = -1
        tag_list = []
        with open(sms_red_fp, 'r') as fin:
            for line in fin.readlines():
                info_list = line.split('\t')
                if pair_idx != -1 and int(info_list[0]) != pair_idx:
                    tag_list += self.splitTime(timestamp)
                    timestamp = []
                pair_idx = int(info_list[0])
                #timestamp.append(time.mktime(time.strptime(info_list[1], "%Y-%m-%d %H:%M:%S")))
                timestamp.append(time.mktime(time.strptime(info_list[1], "%Y/%m/%d %H:%M")))
            tag_list += self.splitTime(timestamp)
        true_tag_list = []
        with open(sms_tag_fp, 'r') as fin:
            for line in fin.readlines():
                true_tag_list.append(int(line.strip()))
        test_start = int(PropertiesUtil.getProperty('PARAMETER', 'test_index_start'))
        test_end = int(PropertiesUtil.getProperty('PARAMETER', 'test_index_end'))
        self.printaccuracy(true_tag_list[test_start:test_end], tag_list[test_start:test_end])

        with open(sms_red_fp, 'r') as fin, open(sms_time_fp, 'w') as fout:
            idx = 0
            for line in fin.readlines():
                fout.write(line.strip() + ',' + str(tag_list[idx]) + '\n')
                idx += 1

    def splitTime(self, timestamp):
        dur_time_rate = float(PropertiesUtil.getProperty('PARAMETER', 'during_time_rate'))
        dur_time_thresh = int(PropertiesUtil.getProperty('PARAMETER', 'during_time_threshold'))
        tag_list = []
        during = [timestamp[i + 1] - timestamp[i] for i in range(len(timestamp) - 1)]
        during_sort = sorted(during, reverse=True)
        acc_num = len(during) * (1 - dur_time_rate)
        add_num = 0
        split_time = 0
        for dur in during_sort:
            add_num += 1
            if add_num > acc_num:
                split_time = dur
                break
        tag_list.append(1)
        for dur in during:
            if dur >= split_time or dur >= dur_time_thresh:
                tag_list[-1] = 2
                tag_list.append(1)
            else:
                tag_list.append(0)
        return tag_list

    def printaccuracy(self, true_tag, predict_tag):
        accuracy = accuracy_score(true_tag, predict_tag)
        print '*******模型的测试结果*********'
        print '\n'
        print 'accuracy is %f' % (accuracy)
        print 'score report is \n'
        print classification_report(true_tag, predict_tag)
        print 'confusion is \n'
        print confusion_matrix(true_tag, predict_tag)
        print '\n'


