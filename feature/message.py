#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.append("../")
from util.PropertiesUtil import PropertiesUtil
from extractor import Extractor
import chardet
import time
import jieba.posseg as pseg
from gensim.models import word2vec

class SMSContent(Extractor):
    def __init__(self):
        Extractor.__init__(self)
        self.stop = [line.strip() for line in open(PropertiesUtil.getProperty('PATH','stopword_fp'), 'r').readlines()]
        self.model = None

    def get_feature_num(self):
        return 302

    def get_cutword_list(self, nodes):
        sms_list = []
        for nd in nodes:
            seg_list = pseg.cut(nd[4])
            seg_list = [word.word.strip().encode('utf-8') for word in seg_list if word.flag[0] != 'x']
            seg_list = [word for word in seg_list if word not in self.stop]
            sms_list.append(seg_list)
        self.model = word2vec.Word2Vec(sms_list, size=100, min_count = 1)

    def extract_all(self, nodes):
        features = []
        pair_idx = -1
        sms_list = []
        self.get_cutword_list(nodes)
        nodes.append(None)
        for nd in nodes:
            if nd == None or pair_idx != -1 and nd[0] != pair_idx:
                features += self.extract_content(sms_list)
                sms_list = []
                if nd == None:
                    break
            pair_idx = nd[0]
            sms_list.append(nd[4])
        return features

    def extract_content(self, sms_list):
        sliding_window = int(PropertiesUtil.getProperty('PARAMETER', 'sliding_window'))
        pseg_list = []
        features = list()
        for sms in sms_list:
            seg_list = pseg.cut(sms)
            seg_list = [word.word.strip().encode('utf-8') for word in seg_list if word.flag[0] != 'x']
            seg_list = [word for word in seg_list if word not in self.stop]
            pseg_list.append(seg_list)
        for i in range(len(pseg_list)):
            forward = list()
            for j in range(max(0, i - sliding_window), i):
                forward += pseg_list[j]
            forward_embedding = self.get_word2vec(self.model, forward)
            backward = list()
            for j in range(i + 1, min(len(pseg_list), i + sliding_window)):
                backward += pseg_list[j]
            backward_embedding = self.get_word2vec(self.model, backward)
            word_embedding = self.get_word2vec(self.model, pseg_list[i])
            shared_num1 = self.get_shared_word(forward, pseg_list[i])
            shared_num2 = self.get_shared_word(backward, pseg_list[i])
            feature = [shared_num1, shared_num2]
            feature += forward_embedding
            feature += word_embedding
            feature += backward_embedding
            features.append(feature)
        return features

    def get_word2vec(self, model, word_list):
        if len(word_list) == 0:
            return [0 for i in range(100)]
        embeddings = model[word_list[0]]
        for i in range(1, len(word_list)):
            embedding = model[word_list[i]]
            for dim in range(100):
                embeddings[dim] += embedding[dim]
        embeddings = [num / len(word_list) for num in embeddings]
        return embeddings

    def get_shared_word(self, wordlist1, wordlist2):
        length = min(len(wordlist1), len(wordlist2))
        if length == 0:
            return 0
        shared_num = 0
        for word in wordlist1:
            if word in wordlist2:
                shared_num += 1
        return shared_num * 1.0 / length

if __name__ == '__main__':
    SMSContent().extract()