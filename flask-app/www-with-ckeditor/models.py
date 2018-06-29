#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: xie
# @Date:   2018-06-02 16:50:07
# @Last Modified time: 2018-06-13 16:30:53

from app import db
import uuid,time,json

def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

def created_at():
    return '%d'%(int(time.time()))

class News(db.Model):
    __tablename__='news'
    id=db.Column(db.String(100),primary_key=True,default=next_id)
    name=db.Column(db.String(100),nullable=False)
    content=db.Column(db.Text,nullable=False)
    created_at=db.Column(db.String(50),nullable=False,default=created_at())
    def __repr__(self):
        return json.dumps(dict(id=self.id,name=self.name,content=self.content,created_at=self.created_at))

class Users(db.Model):
    __tablename__='users'
    id=db.Column(db.String(100),primary_key=True,default=next_id)
    name=db.Column(db.String(50),nullable=False)
    passwd=db.Column(db.String(50),nullable=False)
    admin=db.Column(db.Boolean,nullable=False)
    created_at=db.Column(db.String(50),nullable=False,default=created_at())


class Others(db.Model):
    __tablename__='others'
    id=db.Column(db.String(100),primary_key=True,default=next_id)
    name=db.Column(db.String(100),nullable=False)
    content=db.Column(db.Text,nullable=False)
    def __repr__(self):
        return json.dumps(dict(id=self.id,name=self.name,content=self.content))