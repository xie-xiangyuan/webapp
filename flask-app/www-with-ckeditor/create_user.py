#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: xie
# @Date:   2018-06-08 14:06:40
# @Last Modified time: 2018-06-08 16:50:13

from models import Users
from app import db

user=Users(name='admin',passwd='Admin@123',admin=True)
db.session.add(user)
db.session.commit()

