#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: xie
# @Date:   2018-04-04 13:56:24
# @Last Modified time: 2018-04-09 16:14:58

import uuid,time
from orm import Model,int_field,str_field,bool_field,text_field,float_field

def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

class User(Model):
    __table__='users'
    id=str_field(is_primarykey=True,default=next_id,ddl='varchar(50)')
    email=str_field(ddl='varchar(50)')
    passwd=str_field(ddl='varchar(50)')
    admin=bool_field()
    name=str_field(ddl='varchar(50)')
    image=str_field(ddl='varchar(500)')
    created_at=float_field(default=time.time)

class News(Model):
    __table__='news'
    id=str_field(is_primarykey=True,default=next_id, ddl='varchar(50')
    user_id = str_field(ddl='varchar(50)')
    user_name = str_field(ddl='varchar(50)')
    user_image = str_field(ddl='varchar(500)')
    name = str_field(ddl='varchar(50)')
    summary = str_field(ddl='varchar(200)')
    content = text_field()
    created_at = float_field(default=time.time)

class Others(Model):
    __table__='others'
    id=str_field(is_primarykey=True,default=next_id, ddl='varchar(50')
    image=str_field(ddl='varchar(500')
    name=str_field(ddl='varchar(50')
    summary=str_field(ddl='varchar(200')
    content=text_field()
