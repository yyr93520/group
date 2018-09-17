#! /usr/bin/python
# -*- coding: utf-8 -*-
import time
from util.PropertiesUtil import PropertiesUtil

def during_time(msg_file):
    fin = open(msg_file, 'r')
    pair_dict = {}
    for line in fin.readlines():
        info_list = line.split('\t')
        if cmp(info_list[0], info_list[1]) < 0:
            user = info_list[0] + '@' + info_list[1]
        else:
            user = info_list[1] + '@' + info_list[0]
        if not pair_dict.has_key(user):
            pair_dict[user] = []
        timestamp = time.mktime(time.strptime(info_list[2], "%Y-%m-%d %H:%M:%S"))
        pair_dict[user].append(timestamp)
    during_num = {}
    for user in pair_dict:
        timestamp = sorted(pair_dict[user], reverse=True)
        during = [timestamp[i + 1] - timestamp[i] for i in range(len(timestamp) - 1)]
        for dur in during:
            dur_int = round(dur / 1800)
            if not during_num.has_key(dur_int):
                during_num[dur_int] = 0
            during_num[dur_int] += 1
    print during_num

def avg_during_time():
    sms_red_fp = PropertiesUtil.getProperty('PATH', 'sms_red_fp')
    fin = open(sms_red_fp, 'r')
    timestamp = []
    pair_idx = -1
    for line in fin.readlines():
        info_list = line.split('\t')
        if pair_idx != -1 and int(info_list[0]) != pair_idx:
            during_dist(timestamp)
            timestamp = []
        pair_idx = int(info_list[0])
        timestamp.append(time.mktime(time.strptime(info_list[1], "%Y-%m-%d %H:%M:%S")))

    during_dist(timestamp)

def during_dist(timestamp):
    during = [timestamp[i + 1] - timestamp[i] for i in range(len(timestamp) - 1)]
    during_num = {}
    for dur in during:
        dur_int = round(dur / 60)
        if not during_num.has_key(dur_int):
            during_num[dur_int] = 0
        during_num[dur_int] += 1
    print during_num

def pair_num(msg_file):
    fin = open(msg_file, 'r')
    pair_dict = {}
    for line in fin.readlines():
        info_list = line.split('\t')
        if cmp(info_list[0], info_list[1]) < 0:
            user = info_list[0] + '@' + info_list[1]
        else:
            user = info_list[1] + '@' + info_list[0]
        if not pair_dict.has_key(user):
            pair_dict[user] = 0
        pair_dict[user] += 1
    msg_num = {}
    for user in pair_dict:
        num_int = round(pair_dict[user] * 1.0 / 50)
        if not msg_num.has_key(num_int):
            msg_num[num_int] = 0
        msg_num[num_int] += 1
    print msg_num

def one_num(msg_file, id):
    fin = open(msg_file, 'r')
    msg_dict = {}
    for line in fin.readlines():
        info_list = line.split('\t')
        user = info_list[id]
        if not msg_dict.has_key(user):
            msg_dict[user] = 0
        msg_dict[user] += 1
    msg_num = {}
    for user in msg_dict:
        num_int = round(msg_dict[user] * 1.0 / 100)
        if not msg_num.has_key(num_int):
            msg_num[num_int] = 0
        msg_num[num_int] += 1
    print msg_num

def msg_len(msg_file):
    fin = open(msg_file, 'r')
    len_dict = {}
    for line in fin.readlines():
        info_list = line.split('\t')
        msg_l = len(info_list[3].decode('utf-8'))
        if not len_dict.has_key(msg_l):
            len_dict[msg_l] = 0
        len_dict[msg_l] += 1
    return len_dict

if __name__ == '__main__':
    avg_during_time()