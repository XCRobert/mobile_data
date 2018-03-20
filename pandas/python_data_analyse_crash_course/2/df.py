#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:    xurongzhong#126.com wechat:pythontesting qq group:630011153
# CreateDate: 2018-3-14
# df.py

import pandas as pd
import numpy as np

scientists = pd.read_csv('../data/scientists.csv')
print(scientists[scientists['Age'] > scientists['Age'].mean()])