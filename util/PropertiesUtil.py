#! /usr/bin/python
# -*- coding: utf-8 -*-

import ConfigParser
import os

class PropertiesUtil(object):

    config = ConfigParser.ConfigParser()
    config.read(os.path.join(os.path.abspath('..'), 'community.ini'))

    @staticmethod
    def getProperty(section, option):
        return PropertiesUtil.config.get(section, option)

    @staticmethod
    def setProperty(section, option, value):
        PropertiesUtil.config.set(section, option, value)