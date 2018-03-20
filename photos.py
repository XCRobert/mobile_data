#/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:    xurongzhong#126.com wechat:pythontesting qq:37391319
# CreateDate: 2018-3-15
# photos.py

import os

import cv2
import numpy as np
from PIL import Image, ImageDraw

def mark_image(filename, dst, poses):
    '''
    files： 文件列表
    dst： 目的文件目录
    poses: 为颜色跟对应的坐标(left, top, right,  bottom)。 
    比如{"green":(1,1,99,100)}
    '''
    image = Image.open(filename)
    d = ImageDraw.Draw(image, 'RGBA')
    for color in poses:
        d.rectangle(poses[color],outline=color)   
    image.save(dst)

def mark_images(files, out,shenzhens, beijings):
    for filename in files:
        name = os.path.basename(filename)
        sz = shenzhens.get(name)
        bj = beijings.get(name)  
        bj_sz_photo_compare(sz,bj,filename,prefix=out)

def bj_sz_photo_compare(sz,bj,filename,prefix="_"):
    poses = {}
    if sz:
        poses["green"] = sz
        print("shenzhen:",sz)
    else:
        print("shenzhen: Can not recognize!",)
    if bj:
        poses["red"] = bj
        print("beijing:",bj)
    else:
        print("beijing: Can not recognize!",)
    name = os.path.basename(filename)
    if type(name) == bytes:
        name = name.decode()   
    new_name = "{}{}".format(prefix,name)
    print("Please see {}".format(new_name))
    mark_image(filename,new_name,poses)    
 
def rotateImage(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result

def rotate2(files, dst, value=90):
    for file_ in files:
        img = cv2.imread(file_,0)
        result = rotateImage(img, value)
        cv2.imwrite("{}{}{}".format(dst, os.sep, os.path.basename(file_)), 
result) 
