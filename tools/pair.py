#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:    xurongzhong#126.com 技术支持qq群：144081101
# CreateDate: 2018-1-8 
# check_md5.py

import argparse

from data_common import *
    
parser = argparse.ArgumentParser()
parser.add_argument('directory', action="store", help=u'目录')
parser.add_argument('-d', action="store_true", default=False, help=u'是否删除文件')
parser.add_argument('-type1', action="store", dest="type1", default="ir")
parser.add_argument('-type2', action="store", dest="type2", default="depth")
parser.add_argument('--version', action='version',
                    version='%(prog)s 1.1 Rongzhong xu 2018 04 02')
options = parser.parse_args()

check_pair_file(options.directory, options.type1, options.type2, options.d)