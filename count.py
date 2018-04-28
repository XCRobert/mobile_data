#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:    xurongzhong#126.com wechat:pythontesting qq:37391319
# CreateDate: 2018-1-8
# data_common.py

import numpy as np
from sklearn.metrics import roc_curve
from data_common import output_file

def roc(score,label, fprs=np.arange(0.05, 0, -0.01), output='output/roc.txt'):
    scores_ori = np.loadtxt(score, dtype=np.float32, delimiter='\n')
    labels_ori = np.loadtxt(label, dtype=np.int32, delimiter='\n')
    assert(len(scores_ori) == len(labels_ori))
    
    scores = scores_ori[scores_ori >= 0]
    labels = labels_ori[scores_ori >= 0]

    roc_fpr, roc_tpr, roc_thresholds = roc_curve(
        labels, scores, pos_label=1, drop_intermediate=False)
    
    fprs = np.arange(0.05, 0, -0.01)
    tpr_k_score = []
    th_k_score = []
    for fpr_ratio in fprs:
        idx = np.argmin(np.abs(roc_fpr - fpr_ratio))
        tpr = roc_tpr[idx]
        th = roc_thresholds[idx]
        tpr_k_score.append(tpr)
        th_k_score.append(th)
    with open(output, 'w') as f:
        print("total_num: {}".format(len(scores_ori)),file=f)
        print("valid_num: {}".format( len(scores)),file=f)        
        print("fpr    | "+" | ".join('{:.3f}'.format(i) for i in fprs),file=f)
        print("|".join("  :-:  " for i in range(len(fprs)+1)),file=f)
        print("tpr(%) | "+" | ".join('{:.2f}'.format(i*100) for i in tpr_k_score),file=f)
        print("thres  | "+" | ".join('{:.3f}'.format(i) for i in th_k_score),file=f)
        

