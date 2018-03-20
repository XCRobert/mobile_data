#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
import multiprocessing
from pathlib import Path

import data_common

def consumer(queue, results, lock):
    while True:
        item = queue.get()
        if item is None:
            break        
        name = os.path.basename(item)
        md5 = data.common.get_md5(item, is_file=True)
        
        with lock:
            if md5 in results:
                print("Same md5", results[md5], name)
            else:
                results[md5] =[]
            results[md5] = results[md5] + [name]


if __name__ == '__main__':
    
    process = []
    queue = multiprocessing.Queue()
    results = multiprocessing.Manager().dict()
    lock = multiprocessing.Lock()
    if multiprocessing.cpu_count() < 3:
        number = multiprocessing.cpu_count()
    else:
        number = multiprocessing.cpu_count() - 1
    
    # Launch the consumer process
    for i in range(number):
        t = multiprocessing.Process(
            target=consumer,args=(queue, results, lock))
        t.daemon=True
        process.append(t)
    
    for i in range(number):
        process[i].start()
    
    src = r'/home/andrew/test'
    p = Path(src)   
    for item  in p.glob('**/*.jpg'):
        queue.put(str(item))
        
    for i in range(number + 1):
        queue.put(None) 
        
    for i in range(number):
        process[i].join()
        
       
    f = open("md5_files.txt",'w')    
    for item in dict(results):
        if len(results[item]) > 1:
            f.write("{},{}\n".format(item,results[item]))
        
