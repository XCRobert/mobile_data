#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:    xurongzhong#126.com wechat:pythontesting qq:37391319
# CreateDate: 2018-3-15
# rotate.py
import glob
import os 

from photos import rotate

src = r'/home/andrew/code/mobile_data/tools/1'
dst = r'/home/andrew/code/mobile_data/tools/True'

common = glob.glob('{}{}*.*'.format(src, os.sep))  
rotate(common, dst)

#dual = glob.glob('/home/andrew/code/data/双通无人脸数据/test/*.*')   
#rotate(dual, '/home/andrew/code/data/双通无人脸数据/rotate/')
