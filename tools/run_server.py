#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author:    xurongzhong#126.com 
# CreateDate: 2018-3-31

import argparse
import shutil
import os
import subprocess
import time
import re

import massedit

import data_common
import servers
import count

description = '''

功能：执行比对测试

活体示例：
python3 run_server.py liveness -t batch1.7.5
python3 run_server.py liveness -t batch1.7.6
python3 run_server.py liveness -t base
python3 run_server.py liveness -t bug

landmark示例： 
$ python3 run_server.py landmark -d /home/andrew/code/tmp/sensetime -w
'''

parser = argparse.ArgumentParser(description=description,
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('test_type', action="store", help=u'测试类型')
parser.add_argument('-d', action='store', dest='directory', default=None,
                    help='数据集目录') 
parser.add_argument('-b', action='store', dest='base', 
                    default='/opt/test_tools/base/faceunlock_test_general_meil',
                    help='比对工具目录') 
parser.add_argument('-t', action='store', dest='data_type', default='',
                    help='数据集类型')     
parser.add_argument('-w', action="store_true", default=False, help=u'是否等待结束')
parser.add_argument('-o', action='store', dest='output', default='output',
                    help='输出目录')
parser.add_argument('--version', action='version',
                    version='%(prog)s 1.0 Rongzhong xu 2018 04 26')
options = parser.parse_args()

types = {
    "gaze": {
        'file_type':'ir',
        'name': 'gaze_mn',
        'process': 'sample_gaze_mn',        
        'flag':'/no_gaze/',
        'cmd':"nohup ./run -f output/files.txt > gaze.log 2>&1 &",
        'base':'/home/andrew/code/data/tof/base_test_data/vivo-gaze',
        'little':'/home/andrew/code/data/tof/little_test_data/little_gaze',    
        },
    
    "liveness": {
        'file_type':'ir,depth',
        'name': 'liveness',
        'process': 'sample_liveness',
        'flag':'photo/',
        'cmd': "nohup ./run -l output/files.txt > live.log 2>&1 & ",
        'bug':"/home/andrew/code/data/tof/bug/liveness",
        'base':'/home/andrew/code/data/tof/base_test_data/vivo-liveness',
        'batch1.7.5':'/home/andrew/code/data/tof/vivo3D_batch_test/demo_1.7.5_test',
        'batch1.7.6':'/home/andrew/code/data/tof/vivo3D_batch_test/demo_1.7.6_test',
        'little':'/home/andrew/code/data/tof/little_test_data/little_hacker',                
        },
    
    "landmark":{
        'file_type':'ir',
        'name': 'detect',
        'process': 'sample_align',
        'flag':'/little_photo/',
        'cmd':"nohup ./run -m output/files.txt > landmark.log 2>&1 &",
        },
}

tool = options.base
now = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())    
if options.directory is None:
    if not options.data_type:
        print("data_type不能为空")
        exit(1)
    options.directory = types[options.test_type][options.data_type]
    
file_name = "{}{}{}".format(tool, os.sep, "output/files.txt")
label_name = "{}{}{}".format(tool, os.sep, "output/labels.txt")
config_name = "{}{}{}".format(tool, os.sep, "config.json")
data_common.get_filelistandlabel(
    options.directory,
    types[options.test_type]['flag'],
    filetype=types[options.test_type]['file_type'],
    file_name=file_name,
    label_name=label_name)

configs = open(config_name).read()

search = re.search('{0}.*?(\d+.\d+.\d+)'.format(types[options.test_type]['name']),
                    configs)
if not search:
    print("Error: Can not find version!")
    exit(1)
version = search.group(1)
print(types[options.test_type]['name'], version)
cmd1 = "cd {}".format(tool)
directory = "{0}{1}result{1}{2}-{3}-{4}-{5}".format(
    tool, os.sep, options.test_type, now, options.data_type, version)
data_common.check_directory(directory)
shutil.copyfile(file_name, 
                "{}{}{}".format(directory, os.sep,os.path.basename(file_name)))
shutil.copyfile(label_name,
                "{}{}{}".format(directory, os.sep,os.path.basename(label_name)))
shutil.copyfile(config_name, 
                "{}{}{}".format(directory, os.sep,os.path.basename(config_name)))
cmd = "{} && {}".format(cmd1,types[options.test_type]['cmd'])
print(cmd)
subprocess.call(cmd,shell=True)

print("Please see result in {}".format(directory))

# wait for result
if not options.w:
    exit(0)

# anlyse result
result = "{0}{1}{2}{1}{2}_output%files.txt.csv".format(
    tool, os.sep, options.test_type)
servers.wait_until_stop(types[options.test_type]['process'])
new_result = "{0}{1}{2}-result.csv".format(directory, os.sep, version)
shutil.copyfile(result, new_result)

if options.test_type != 'verify':
    values = "{0}{1}{2}-values.csv".format(directory, os.sep, version)
    maps = data_common.concat_file(new_result, file_name, sep=',')
    data_common.output_file(values, maps)    

if options.test_type == 'liveness':
    new_result_ = "{0}{1}{2}-result_.csv".format(directory, os.sep, version)
    shutil.copyfile(result, new_result_)
    cmd = "sed -i  's#-1#1#' {}".format(new_result_)
    subprocess.call(cmd,shell=True)
     
    if options.data_type == 'base':
        replace = '/home/andrew/code/data/tof/base_test_data/vivo-liveness/'
    else:
        replace = ''
    error_name = "{0}{1}{2}-result.xlsx".format(directory, os.sep, version)
    servers.get_liveness_server_result(new_result, file_name, label_name, 
        replace=replace, error_name=error_name)

    roc = "{0}{1}{2}-roc.txt".format(directory, os.sep, version)
    count.roc(new_result_, label_name, output=roc)

if options.test_type == 'gaze':
    fprs = [0.3,0.25,0.2,0.15,0.1,0.05,0.02,0.01,0.001]
    roc = "{0}{1}{2}-roc.txt".format(directory, os.sep, version)
    count.roc(result, label_name, fprs=fprs, output=roc, )    



    
