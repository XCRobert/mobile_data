#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:    xurongzhong#126.com 
# CreateDate: 2018-4-18 
# check_md5.py

import argparse
import time

import pandas as pd

import servers
import data_common

'''
调用示例：

$ python3 get_verify_server_result.py /opt/test_tools/base/faceunlock_test_general_meil/result/i_enroll.txt /opt/test_tools/base/faceunlock_test_general_meil/result/i_real.txt /opt/test_tools/base/faceunlock_test_general_meil/result/verify452-3.56.csv 
'''

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('names', action="store", help=u'测试人名列表文件')
    parser.add_argument('files', action="store", help=u'测试图片列表文件')
    parser.add_argument('scores', action="store", help=u'服务器verify结果')
    parser.add_argument('-d', action="store_true", default=False, help=u'是否批量')
    parser.add_argument('-s', action="store", dest="score", default=0.7, 
                        help=u'分数的门限')
    parser.add_argument('-o', action="store", dest="output_dir",
                        default="./", help=u'结果输出目录')
    parser.add_argument('-f', action="store", dest="replace_file",
                        default="/home/andrew/code/data/tof/base_test_data/vivo-verify-452/./",
                        help=u'文件名需要替换为空的部分')    
    parser.add_argument('-n', action="store", dest="replace_name",
                        default="output/enroll_list/", help=u'人名需要替换为空的部分')     
    parser.add_argument('--version', action='version',
                        version='%(prog)s 1.1 Rongzhong xu 2018 03 22')
    options = parser.parse_args()
    
    if options.d:
        servers.get_verify_server_result(
            options.names, options.files, options.scores,
            score=options.score, output_dir=options.output_dir,
            replace_file=options.replace_file,
            replace_name=options.replace_name,)  
        exit(0)
    
    df, real_photos = servers.load_verify_server_result(
        options.names, options.files, options.scores,
        replace_file=options.replace_file,
        replace_name=options.replace_name)    
    
    others = []
    others_num = 0
    selfs = []
    selfs_num = 0
    for person in df.index:
        print("index:", person)
        print(time.ctime())
        row = df.loc[person]
        row.index = [real_photos['person'], real_photos['filename']]
        print(row)
        self_list = row[person]
        selfs_num = selfs_num + len(self_list)
        self_ = self_list[(self_list<=0.9) & (self_list>-1)]
        for item in self_.index:
            selfs.append((item, self_[item]))
        #print(self_error)
        other_list = row.drop(person,level=0)
        others_num = others_num + len(other_list)
        other_ = other_list[other_list>=0.7]
        for item in other_.index:
            others.append([person,item[1], other_.loc[item]])    
        #print(other_error)
                
    df_person_errors = pd.DataFrame(selfs,columns=['filename','score'])
    df_other_errors = pd.DataFrame(others,columns=['person','filename','score'])
    
    values = [0.70, 0.71, 0.72, 0.73, 0.74, 0.75, 0.76, 0.77, 0.78, 0.79, 0.80,
              0.81, 0.82, 0.83, 0.84, 0.85, 0.86, 0.87, 0.88, 0.89, 0.90]
    
    results = []
    for value in values:
        result = servers.get_verify_frr_far(
            selfs_num, others_num, df_person_errors, df_other_errors, 'score',
            value)
        results.append([value, *result])
        
    df4 = pd.DataFrame(
        results, 
        columns=["Threshold","FAR", "FRR", "number","real_number", "frr_number",
                 "no_number", "far_number"])
    
    df4.to_csv("verify_far_frr.csv",index=None)    