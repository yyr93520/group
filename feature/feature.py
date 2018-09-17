#! /usr/bin/python
# -*- coding: utf-8 -*-


import hashlib
import random
from os.path import isfile
import ConfigParser
import sys
sys.path.append("../")
import numpy as np
from scipy.sparse import csr_matrix, hstack, vstack
from util.PropertiesUtil import PropertiesUtil

class Feature(object):

    @staticmethod
    def save_feature(features, feature_file):
        for feature in features:
            if feature is None:
                feature_file.write('\n')
            elif isinstance(feature, list):
                feature = [str(i) for i in feature]
                feature = ' '.join(['%s:%s' % (kv[0], kv[1]) for kv in enumerate(feature) if kv[1] != 0])
                feature_file.write('%s\n' % feature)
            elif isinstance(feature, dict):
                feature = ' '.join(['%s:%s' % (key, feature[key]) for key in feature])
                feature_file.write('%s\n' % feature)
            else:
                feature_file.write('0:%s\n' % feature)

    @staticmethod
    def merge_file(feature_pt, feature_name, data_set_name, part_num):
        features = None
        for part_id in range(part_num):
            features_part_fp = '%s/%s.%s.smat.%03d_%03d' % (feature_pt, feature_name, data_set_name, part_num, part_id)
            features_part = Feature.load(features_part_fp)
            if features is None:
                features = features_part
            else:
                features = Feature.merge_row(features, features_part)

        features_fp = '%s/%s.%s.smat' % (feature_pt, feature_name, data_set_name)
        Feature.save_smat(features, features_fp)

    @staticmethod
    def merge_features(feature_pt, feature_name_lst):
        features = None
        for i in range(len(feature_name_lst)):
            feature_fp = '%s/%s.txt' % (feature_pt, feature_name_lst[i])
            feature = Feature.load(feature_fp)
            if features is None:
                features = feature
            else:
                features = Feature.merge_col(features, feature)
        feature_fp = '%s/%s.txt' % (feature_pt, '_'.join(feature_name_lst))
        Feature.save_txt(features, feature_fp)

    @staticmethod
    def sample_row(features, indexs):
        features_sampled = features[indexs, :]
        (row_num, col_num) = features_sampled.shape
        return features_sampled

    @staticmethod
    def sample_col(features, indexs):
        features_sampled = features[:, indexs]
        (row_num, col_num) = features_sampled.shape

        return features_sampled

    @staticmethod
    def merge_row(feature_1, feature_2):
        """
        merge features made split by row
        :param feature_1: the first part of features
        :param feature_2: the second part of features
        :return: feature matrix
        """
        features = vstack([feature_1, feature_2])
        (row_num, col_num) = features.shape

        return features

    @staticmethod
    def merge_col(features_1, features_2):
        """
        merge features made split by column
        :param features_1: the first part of features
        :param features_2: the second part of features
        :return: feature matrix
        """
        features = hstack([features_1, features_2])
        (row_num, col_num) = features.shape
        return features

    @staticmethod
    def load(ft_fp):
        """
        WARNING: the NPZ file is buffer files, be careful of these files
        :param ft_fp: features file path
        :return: matrix of features
        """
        has_npz = isfile('%s.npz' % ft_fp)
        if has_npz:
            features = Feature.load_npz(ft_fp)
        else:
            features = Feature.load_txt(ft_fp)
            #Feature.save_npz(features, ft_fp)
        return features

    @staticmethod
    def load_npz(ft_fp):
        loader = np.load('%s.npz' % ft_fp)
        features = csr_matrix((loader['data'],
                               loader['indices'],
                               loader['indptr']),
                              shape=loader['shape'])

        return features

    @staticmethod
    def save_npz(features, ft_fp):
        """
        save features to disk in binary format
        :param features:
        :param ft_fp:
        :return:
        """
        np.savez(ft_fp,
                 data=features.data,
                 indices=features.indices,
                 indptr=features.indptr,
                 shape=features.shape)

    @staticmethod
    def load_txt(ft_fp):
        """
        load features from disk, the format:
            row_num col_num
            f1_index:f1_value f2_index:f2_value ...
        """
        data = []
        indice = []
        indptr = [0]
        f = open(ft_fp)
        [row_num, col_num] = [int(num) for num in f.readline().strip().split()]
        for line in f:
            line = line.strip()
            subs = line.split()
            for sub in subs:
                [f_index, f_value] = sub.split(":")
                f_index = int(f_index)
                f_value = float(f_value)
                data.append(f_value)
                indice.append(f_index)
            indptr.append(len(data))
        f.close()
        #print indptr
        features = csr_matrix((data, indice, indptr), shape=(row_num, col_num), dtype=float)
        return features

    @staticmethod
    def save_txt(features, ft_pt):
        """
        save features to disk in SMAT format
        :param features: the matrix of features
        :param ft_pt: features file path
        :return: none
        """
        np_arr = features.toarray()
        np.savetxt(ft_pt, np_arr)

    @staticmethod
    def load_all(feature_pt, feature_names, rawset_name, will_save=False):
        index_begin = 0
        features = None
        for index in reversed(range(1, len(feature_names))):
            f_names_s = '|'.join(feature_names[0:index + 1]) + '|' + rawset_name
            f_names_md5 = hashlib.md5(f_names_s).hexdigest()
            if isfile('%s/md5_%s.smat.npz' % (feature_pt, f_names_md5)):
                index_begin = index
                features = Feature.load('%s/md5_%s.smat' % (feature_pt, f_names_md5))
                break

        if 1 > index_begin:
            features = Feature.load('%s/%s.%s.smat' % (feature_pt, feature_names[0], rawset_name))
        for index in range(index_begin + 1, len(feature_names)):
            features = Feature.merge_col(features,
                                         Feature.load(
                                             '%s/%s.%s.smat' % (feature_pt, feature_names[index], rawset_name)))

        features = features.tocsr()

        if will_save and (index_begin < len(feature_names) - 1):
            f_names_s = '|'.join(feature_names) + '|' + rawset_name
            f_names_md5 = hashlib.md5(f_names_s).hexdigest()
            Feature.save_npz(features, '%s/md5_%s.smat' % (feature_pt, f_names_md5))
        return features

    @staticmethod
    def balance_index(indexs, labels, positive_rate):
        """
        balance indexs to adjust the positive rate
        :param indexs: index vector to sample raw data set
        :param labels: label vector of raw data set
        :param positive_rate: positive rate
        :return: index vector after balanced
        """
        if positive_rate < 1e-6 or positive_rate > 1. - 1e-6:
            return indexs
        pos_indexs = [index for index in indexs if labels[index] == 1.]
        neg_indexs = [index for index in indexs if labels[index] == 0.]
        origin_rate = 1.0 * len(pos_indexs) / len(indexs)

        if origin_rate < positive_rate:
            pos_indexs, neg_indexs = neg_indexs, pos_indexs
            origin_rate = 1.0 - origin_rate
            positive_rate = 1.0 - positive_rate

        k = (1. - positive_rate) * origin_rate / positive_rate / (1 - origin_rate)

        balance_indexs = pos_indexs
        while k > 1e-6:
            if k > 1. - 1e-6:
                balance_indexs.extend(neg_indexs)
            else:
                balance_indexs.extend(random.sample(neg_indexs, int(k * len(neg_indexs))))
            k -= 1.
        pos_indexs = [index for index in balance_indexs if labels[index] == 1.]
        neg_indexs = [index for index in balance_indexs if labels[index] == 0.]
        balanced_rate = 1.0 * len(pos_indexs) / len(balance_indexs)

        return balance_indexs

if __name__ == '__main__':
    feature_pt = PropertiesUtil.getProperty('PATH', 'feature_pt')
    #Feature.merge_features(feature_pt, ['SMSContent', 'SMSLength', 'TimeInterval'])
    Feature.merge_features(feature_pt, ['Tag'])