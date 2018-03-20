#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author:    xurongzhong@126.com wechat:pythontesting qq:37391319
# CreateDate: 2018-3-19

'''
根据bug列表生成统计。
'''
import argparse
import re
import shutil
import os

import requests

def find_address(url, keys):
    print(url)
    result = requests.get(url)
    books = re.findall(r'href="(.*?)" rel="bookmark', result.text)
    #print(set(books))
    valids = []
    for item in set(books):
        flag = False
        for key in keys:
            if key in item:
                flag = True
                break
        if flag:
            valids.append(item)  
    #print(valids)
    return valids

def find_addresses(url, keys):
    result = requests.get(url)
    page_num = re.search(r'/\s+(\d+)\s+Pages', result.text)
    if page_num:
        page_num = int(page_num.group(1))
    urls =[url,]
    # http://www.allitebooks.com/?s=testing
    # http://www.allitebooks.com/page/2/?s=testing
    for i in range(2, page_num + 1):
        urls.append(url.replace('?', '/page/{}/?'.format(i)))
        
    addresses = []
    for address in urls:
        result = find_address(address, keys)
        if result:
            addresses =  addresses + result
        else:
            return addresses
    return addresses
        

parser = argparse.ArgumentParser()
parser.add_argument('keys', action="store", help=u'要查询的关键字，以空格分隔')
parser.add_argument('-d', action="store_true", default=False, help=u'是否下载')
parser.add_argument('-o', action="store", dest="o",
                    default="/home/andrew/code/tmp_books", help=u'输出目录')
parser.add_argument('-y', action="store", dest="year",
                    default=2013, help=u'输出目录')
parser.add_argument('--version', action='version',
                    version='%(prog)s 1.1 Rongzhong xu 2018 03 19')

options = parser.parse_args()
keys = options.keys.split()
print(options.d)

url = "{}{}".format(r"http://www.allitebooks.com/?s=", "+".join(keys))
print(url)
valids = find_addresses(url, keys)
print(valids)        

actuals = []
for file_link in valids:
    result = requests.get(file_link)
    year = re.search(r'Year.*?(\d+)<', result.text).group(1)
    link = re.search('ref="(.*?)" target="_blank"', result.text).group(1)
    print(year, link)
    if int(year) < int(options.year):
        print("skip old files!")
        continue
    
    name = '-{}.'.format(year).join(link.split('/')[-1].split('.'))
    filename = "{}{}{}".format(options.o, os.sep, name) if options.o else name
    print(filename)
    actuals.append("[{0}]({1})".format(name, link))
    
    if options.d:
        r = requests.get(link, stream=True)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)  
        else:
            print("Failed to download {}".format(link))
                
for item in actuals:
    print(item)