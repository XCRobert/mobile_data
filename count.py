#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:    xurongzhong#126.com wechat:pythontesting qq:37391319
# CreateDate: 2018-1-8
# data_common.py

import numpy as np
from sklearn.metrics import roc_curve
from data_common import output_file

def roc(score,label,output='output/roc.txt'):
    fprs = [10**(-p) for p in np.arange(1, 7, 1.)]
    scores = np.loadtxt(score, dtype=np.float32, delimiter='\n')
    labels = np.loadtxt(label, dtype=np.int32, delimiter='\n')

    roc_fpr, roc_tpr, roc_thresholds = roc_curve(
        labels, scores, pos_label=1, drop_intermediate=False)
    
    fprs = [10**(-p) for p in np.arange(1, 7, 1.)]
    tpr_k_score = []
    th_k_score = []
    for fpr_ratio in fprs:
        idx = np.argmin(np.abs(roc_fpr - fpr_ratio))
        tpr = roc_tpr[idx]
        th = roc_thresholds[idx]
        tpr_k_score.append(tpr)
        th_k_score.append(th)
    with open(output, 'w') as fout:
        print("fpr    | "+" | ".join(format(i, '.0e') for i in fprs), file=fout)
        print("|".join("  :-:  " for i in range(len(fprs)+1)), file=fout)
        print("tpr(%) | "+" | ".join('{:.2f}'.format(i*100) for i in tpr_k_score), 
              file=fout)
        print("thres  | "+" | ".join('{:.3f}'.format(i) for i in th_k_score), 
              file=fout)
