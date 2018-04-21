#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:    xurongzhong#126.com 
# CreateDate: 2018-4-18 
# check_md5.py

import pandas as pd
import os
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('labels', action="store", help=u'labels')
parser.add_argument('files', action="store", help=u'测试图片列表文件')
parser.add_argument('scores', action="store", help=u'服务器liveness结果')
parser.add_argument('-s', action="store", dest="score", default=0.7, 
                    help=u'分数的门限')
parser.add_argument('-o', action="store", dest="output",
                    default="live_result.xlsx", help=u'结果输出目录') 
parser.add_argument('--version', action='version',
                    version='%(prog)s 1.0 Rongzhong xu 2018 04 18')
options = parser.parse_args()


cases = {
    "01": "注册",
    "02": "全脸-稳定拍摄",
    "03": "全脸-晃动拍摄",
    "04": "半脸-鼻子以下超出画面",
    "05": "半脸-眉毛以上超出画面",
    "06": "遮挡大部分五官",
    "07": "遮挡部分五官",
    "08": "手机平放桌面",
    "09": "一睁一闭",
    "10": "闭眼(戴墨镜、裸眼、普通眼镜) ",
    "11": "闭眼(戴墨镜、普通眼镜下滑挡住眼睛) ",
    "12": "闭眼(手机晃动)",
    "13": "注视",
    "14": "非注视",
    "15": "侧躺、平躺"}

def rename(name):
    replace = '/home/andrew/code/data/tof/base_test_data/vivo-liveness/'
    type_ = os.path.dirname(name.replace(replace,"").split()[-1])
    last = type_.split('/')[-1]
    if last in cases:
        type_ = type_.replace(last,cases[last])
    return type_


df_score = pd.read_csv(options.scores, header=None, names=['score'])
df_file = pd.read_csv(options.files, header=None, names=['filename'])
df_label = pd.read_csv(options.labels, header=None, names=['label'])

df = pd.concat([df_label, df_score, df_file], axis=1)
df['type'] = df['filename'].apply(rename)
print(df.head())

results =[]

for name, group in df.groupby('type'):
    print(name)
    # 真人识别为假人
    df1 = group.loc[((group['score'] > options.score) & (group['label'] == 0))]
    # 假人识别为真人
    df2 = group.loc[((group['score'] < options.score) & (group['label'] == 1))]
    results.append([name, len(group), len(df1), len(df2)])
    
    
for name, group in df.groupby('label'):
    print(name)
    # 真人识别为假人
    df1 = group.loc[((group['score'] > options.score) & (group['label'] == 0))]
    # 假人识别为真人
    df2 = group.loc[((group['score'] < options.score) & (group['label'] == 1))]
    results.append([name, len(group), len(df1), len(df2)])    

print(results)
# 真人识别为假人
df1 = df.loc[((df['score'] > options.score) & (df['label'] == 0))]
# 假人识别为真人
df2 = df.loc[((df['score'] < options.score) & (df['label'] == 1))]
results.append(["All", len(df), len(df1), len(df2)])
writer = pd.ExcelWriter(options.output)
df1.to_excel(writer, sheet_name='真人识别为假人', index=False)
df2.to_excel(writer, sheet_name='假人识别为真人', index=False)
writer.save()

df3 = pd.DataFrame(results, columns=["类别","总数","真人识别为假人","假人识别为真人"])
df3.to_excel("cat.xls")
