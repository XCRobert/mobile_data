#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:    xurongzhong#126.com 
# CreateDate: 2018-4-18 
# check_md5.py

'''
python3 get_live_server_result.py /opt/test_tools/base/faceunlock_test_general_meil/result/label-live.txt  /opt/test_tools/base/faceunlock_test_general_meil/result/live-files.txt  /opt/test_tools/base/faceunlock_test_general_meil/result/live3.71.csv -s 0.99
'''

import pandas as pd
import os
import argparse

import servers

parser = argparse.ArgumentParser()
parser.add_argument('labels', action="store", help=u'labels')
parser.add_argument('files', action="store", help=u'测试图片列表文件')
parser.add_argument('scores', action="store", help=u'服务器liveness结果')
parser.add_argument('-s', action="store", dest="score", default=0.7, type=float,
                    help=u'分数的门限')
parser.add_argument('-r', action="store_true", default=False, 
                    help=u' 是否用中文用例名字替换数字。')
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
    if last in cases and options.r:
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
    result = servers.get_live_frr_far(group, 'score', options.score, 'label')
    results.append([name, *result])
    
    
for name, group in df.groupby('label'):
    result = servers.get_live_frr_far(group, 'score', options.score, 'label')
    results.append([name, *result])  

# 真人识别为假人
df1 = df.loc[((df['score'] > options.score) & (df['label'] == 0))]
# 假人识别为真人
df2 = df.loc[((df['score'] < options.score) & (df['label'] == 1))]
result = servers.get_live_frr_far(df, 'score', options.score, 'label')
results.append(["All", *result])
writer = pd.ExcelWriter(options.output)
df1.to_excel(writer, sheet_name='真人识别为假人', index=False)
df2.to_excel(writer, sheet_name='假人识别为真人', index=False)
writer.save()

df3 = pd.DataFrame(results, columns=[
    "类别","far", "frr", "总数","真人总数","真人识别为假人", "假人总数", "假人识别为真人","未识别数","未识别率"])
df3.to_excel("cat.xls")

results = []
values = [0.90, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99, 0.999]
for value in values:
    result = servers.get_live_frr_far(df, 'score', value, 'label')
    results.append([value, *result])
    
df4 = pd.DataFrame(results, columns=["Threshold","FAR","FRR","total","real_num","frr_num", "photo_num", "far_num","unknow","unknow_rate"])
df4.to_csv("live_far_frr.csv", index=None)    
    
    
    


