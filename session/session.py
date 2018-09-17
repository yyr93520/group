#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.append("../")
import time
from util.PropertiesUtil import PropertiesUtil
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

class Session(object):

    def __init__(self):
        pass

    def readSMS(self):
        sms_fp = PropertiesUtil.getProperty('PATH', 'sms_fp')
        sms_red_fp = PropertiesUtil.getProperty('PATH', 'sms_red_fp')
        sender_serial = int(PropertiesUtil.getProperty('SERIAL', 'sender'))
        receiver_serial = int(PropertiesUtil.getProperty('SERIAL', 'receiver'))
        time_serial = int(PropertiesUtil.getProperty('SERIAL', 'time'))
        sms_serial = int(PropertiesUtil.getProperty('SERIAL', 'sms'))
        pair_dict = {}
        pair2id = {}
        idx = 0
        with open(sms_fp, 'r') as fin:
            for line in fin.readlines():
                info_list = line.strip().split('  ')
                if cmp(info_list[sender_serial], info_list[receiver_serial]) < 0:
                    user = info_list[sender_serial] + '@' + info_list[receiver_serial]
                else:
                    user = info_list[receiver_serial] + '@' + info_list[sender_serial]
                if not pair2id.has_key(user):
                    pair2id[user] = idx
                    idx += 1
                user_id = pair2id[user]
                if not pair_dict.has_key(user_id):
                    pair_dict[user_id] = []
                #timestamp = time.mktime(time.strptime(info_list[time_serial], "%Y-%m-%d %H:%M:%S"))
                user_sms = {}
                user_sms['time'] = info_list[time_serial]
                user_sms['sms'] = info_list[sms_serial]
                user_sms['sender'] = info_list[sender_serial]
                user_sms['receiver'] = info_list[receiver_serial]
                pair_dict[user_id].append(user_sms)
        with open(sms_red_fp, 'w') as fout:
            for id in pair_dict:
                print pair_dict[id]
                users_sms = sorted(pair_dict[id], key = lambda x : time.mktime(time.strptime(x['time'], "%Y-%m-%d %H:%M:%S")))
                for user_sms in users_sms:
                    fout.write(str(id) + '\t' + user_sms['time'] + '\t' + user_sms['sender']
                               + '\t' + user_sms['receiver'] + '\t' + user_sms['sms'] + '\n')

    def train(self, features):
        assert False, 'Please override function: Session.train()'

    def predict(self, features):
        assert False, 'Please override function: Session.predict()'

    def sessionReduction(self):
        predict_result = self.predict()


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



if __name__ == '__main__':
    session = Session()
    session.timeReduction()