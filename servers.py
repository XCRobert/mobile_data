#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:    xurongzhong#126.com wechat:pythontesting qq:37391319
# CreateDate: 2018-1-8
# datas.py
import time
import os
import subprocess

import pandas as pd

def get_live_frr_far(df,colomn1,score,colomn2):
    
    total = len(df)
    unknow = len(df[df[colomn1] == -1])
    df = df[df[colomn1] != -1]
    real_number = len(df[df[colomn2] == 0])
    photo_number = len(df[df[colomn2] == 1])
    
    # 真人识别为假人
    frr_number = len(df.loc[((df[colomn1] > score) & (df[colomn2] == 0))])
    # 假人识别为真人
    far_number = len(df.loc[((df[colomn1] < score) & (df[colomn2] == 1))])
    frr = 0 if not real_number else frr_number/float(real_number)
    far = 0 if not photo_number else far_number/float(photo_number)
    return (far, frr, total, real_number, frr_number, photo_number, far_number, unknow, unknow/float(total))

def get_gaze_frr_far(df,colomn1,score):
    
    total = len(df)
    unknow = len(df[df[colomn1] == -1])
    df = df[df[colomn1] != -1]
    real_number = len(df.loc[df['filename'].str.contains('/gaze/')])
    no_number = len(df.loc[df['filename'].str.contains('/no_gaze/')])
    
    # 真人识别为假人
    frr_number = len(df.loc[(df['score'] < score) & df['filename'].str.contains('/gaze/')])
    # 假人识别为真人
    far_number = len(df.loc[(df['score'] > score) & df['filename'].str.contains('/no_gaze/')] )
    frr = 0 if not real_number else frr_number/float(real_number)
    far = 0 if not no_number else far_number/float(no_number)
    return (far, frr, total, real_number, frr_number, no_number, far_number, unknow, unknow/float(total))


def load_verify_server_result(names,files,scores, 
    replace_file="/home/andrew/code/data/tof/base_test_data/vivo-verify-452/./",
    replace_name="output/enroll_list/",
    ):

    real_photos = pd.read_csv(files, names=['filename'])
    real_photos['filename'] = real_photos['filename'].apply(
        lambda x:x.replace(replace_file, ''))
    real_photos['person'] =  real_photos['filename'].apply(
        lambda x:x.split('/')[0])
    
    
    persons = pd.read_csv(names,names=['person'])
    persons['person'] = persons['person'].apply(
        lambda x:x.replace(replace_name, ''))
    
    df = pd.read_csv(scores, header=None, engine='c',
                     na_filter=False, low_memory=False)
    df.index = persons['person']
    return df, real_photos


def get_verify_errors(df, real_photos, score):
    
    other_errors = []
    self_errors = []
    for person in df.index:
        print("index:", person)
        print(time.ctime())
        row = df.loc[person]
        row.index = [real_photos['person'], real_photos['filename']]
        self = row[person]
        self_error = self[(self<score) & (self>-1)]
        for item in self_error.index:
            self_errors.append((item, self_error[item]))
        #print(self_error)
        others = row.drop(person,level=0)
        other_error = others[others>=score]
        for item in other_error.index:
            other_errors.append([person,item[1], other_error.loc[item]])    
        #print(other_error)
                
    df_person_errors = pd.DataFrame(self_errors,columns=['filename','score'])
    df_other_errors = pd.DataFrame(other_errors,columns=['person','filename','score'])
    
    return df_person_errors, df_other_errors

def get_verify_frr_far(selfs_num, others_num, df_person_errors, df_other_errors, colomn, score):
    
    frr_num = len(df_person_errors[df_person_errors[colomn] < score])
    far_num = len(df_other_errors[df_other_errors[colomn] > score])
    frr = 0 if not frr_num else frr_num/float(selfs_num)
    far = 0 if not far_num else far_num/float(others_num)
    return (far, frr, selfs_num + others_num, selfs_num, frr_num, others_num, far_num)
    
def get_verify_server_result(
    names,files,scores, score=0.7, output_dir="./",
    replace_file="/home/andrew/code/data/tof/base_test_data/vivo-verify-452/./",
    replace_name="output/enroll_list/",
    ):

    df, real_photos = load_verify_server_result(names,files,scores, 
    replace_file=replace_file,replace_name=replace_name,)
    
    df_person_errors, df_other_errors = get_verify_errors(df, real_photos, score)
    df_person_errors.to_csv('{}{}self_errors.csv'.format(
        output_dir.strip(os.sep), os.sep), index=False)
    df_other_errors.to_csv('{}{}others_errors.csv'.format(
        output_dir.strip(os.sep), os.sep), index=False)
    print(time.ctime())
    
def check_process(name):
    cmd = "ps afx | grep -i '{}' | grep -v grep |wc -l".format(name)
    result = subprocess.check_output(cmd, shell=True)
    return True if int(result.strip()) else False

def wait_until_stop(name,sep=5):
    while check_process(name):
        time.sleep(sep)

def get_liveness_server_result(scores, files, labels, score=0.7,
        replace='/home/andrew/code/data/tof/base_test_data/vivo-liveness/',
        error_name="live_error.xlsx"):
    
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
        type_ = os.path.dirname(name.replace(replace,"").split()[-1])
        last = type_.split('/')[-1]
        if last in cases and replace:
            type_ = type_.replace(last,cases[last])
        return type_
    
    
    df_score = pd.read_csv(scores, header=None, names=['score'])
    df_file = pd.read_csv(files, header=None, names=['filename'])
    df_label = pd.read_csv(labels, header=None, names=['label'])
    
    df = pd.concat([df_label, df_score, df_file], axis=1)
    df['type'] = df['filename'].apply(rename)
    # print(df.head())
    
    results =[]
    
    for name, group in df.groupby('type'):
        result = get_live_frr_far(group, 'score', score, 'label')
        results.append([name, *result])
        
        
    for name, group in df.groupby('label'):
        result = get_live_frr_far(group, 'score', score, 'label')
        results.append([name, *result])  
    
    # 真人识别为假人
    df1 = df.loc[((df['score'] > score) & (df['label'] == 0))]
    # 假人识别为真人
    df2 = df.loc[((df['score'] < score) & (df['label'] == 1))]
    result = get_live_frr_far(df, 'score', score, 'label')
    results.append(["All", *result])
    writer = pd.ExcelWriter(error_name)
    df1.to_excel(writer, sheet_name='真人识别为假人', index=False)
    df2.to_excel(writer, sheet_name='假人识别为真人', index=False)
    
    df3 = pd.DataFrame(results, columns=[
        "类别","far", "frr", "总数","真人总数","真人识别为假人", "假人总数", 
        "假人识别为真人","未识别数","未识别率"])
    df3.to_excel(writer, sheet_name='分类统计', index=False)

    
    results = []
    values = [0.90, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99, 0.999]
    for value in values:
        result = get_live_frr_far(df, 'score', value, 'label')
        results.append([value, *result])
        
    df4 = pd.DataFrame(results, columns=["Threshold","FAR","FRR","total",
        "real_num","frr_num", "photo_num", "far_num","unknow","unknow_rate"]) 
    df4.to_excel(writer, sheet_name='FAR_FRR', index=False)
    writer.save()
    
    
def get_gaze_server_result(scores, files, labels, score=0.5,
        error_name="gaze_error.xlsx"):
    
    values = []    
    for i in range(18):
        values.append(i*0.05+0.1)    

    df_score = pd.read_csv(scores, header=None, names=['score'])
    df_file = pd.read_csv(files, header=None, names=['filename'])
    df_label = pd.read_csv(labels, header=None, names=['label'])
    
    df = pd.concat([df_label, df_score, df_file], axis=1)
    
    df1 = df.loc[(df['score'] < score) & df['filename'].str.contains('/gaze/')]
    df2 = df.loc[(df['score'] > score) & df['filename'].str.contains('/no_gaze/')]
    
    writer = pd.ExcelWriter(error_name)
    df1.to_excel(writer, sheet_name='注视识别为非注视', index=False)
    df2.to_excel(writer, sheet_name='非注视识别为注视', index=False)


    
    results = []
    for value in values:
        result = get_gaze_frr_far(df, 'score', value)
        results.append([value, *result])
    
    df4 = pd.DataFrame(
        results, 
        columns=["Threshold","FAR", "FRR", "number","real_number", "frr_number",
                 "no_number", "far_number","unknow","unknow_rate"])
    
    df4.to_excel(writer, sheet_name='FAR_FRR', index=False)
    writer.save()

    
