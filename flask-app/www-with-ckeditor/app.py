#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: xie
# @Date:   2018-05-31 15:35:17
# @Last Modified time: 2018-06-19 16:23:29

from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
import os,time

app=Flask(__name__)
#app1=Flask(__name__)
app.config.from_object('config')
#app.config['COOKIE_NAME']=' awesome'
#app.config['SECRET_KEY']=os.environ.get('SECRET_KEY')
db=SQLAlchemy(app)

from views import * 

def datetime_filter(t):
    delta=int(time.time())-int(t)
    if delta < 60:
        return '1分钟前'
    if delta < 60*60:
        return '%s分钟前'%(delta//60)
    if delta < 3600*24:
        return '%s小时前'%(delta//3600)
    if delta < 3600*24*7:
        return '%s天前'%(delta//(3600*24))
    dt=time.localtime(int(t))
    return '%s年%s月%s日'%(dt.tm_year,dt.tm_mon,dt.tm_mday)

app.jinja_env.filters['datetime_filter']=datetime_filter

if __name__ == '__main__':
    app.run(debug=True,host='127.0.0.1',port=5000)
    #app1.run(debug=True,host='192.168.101.252',port=5001)
