#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: xie
# @Date:   2018-05-09 14:52:36
# @Last Modified time: 2018-05-10 14:05:57

import os,sys,time,subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

command=[]
process=None

class myFileSystemEventHandler(FileSystemEventHandler):
    def __init__(self,fn):
        super(myFileSystemEventHandler,self).__init__()
        self.restart=fn
    def on_any_event(self,event):
        if event.src_path.endswith('.py'):
            log('python source file changed :%s'%event.src_path)
            self.restart()

def start_process():
    global process,command
    log('start process %s...'%' '.join(command))
    process=subprocess.Popen(command,stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)

def kill_process():
    global process
    if process:
        log('kill process [%s]'%process.pid)
        process.kill()
        process.wait()
        log('process endwith code %s.'%process.returncode)
        process=None

def restart_process():
    kill_process()
    start_process()

def start_watch(path):
    observer=Observer()
    observer.schedule(myFileSystemEventHandler(restart_process),path,recursive=True)
    observer.start()
    log('watching directory %s'%path)
    start_process()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def log(s):
    print('[Monitor]:%s'%s)

if __name__ == '__main__':
    argv=sys.argv[1:]
    if argv is None:
        print('usage:python3 or ./pymonitor your.py...')
        exit(0)
    if argv[0] != 'python3':
        argv.insert(0,'python3')
    command=argv
    path=os.path.abspath('.')
    start_watch(path)