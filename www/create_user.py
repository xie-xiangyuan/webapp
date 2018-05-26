#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: xie
# @Date:   2018-03-29 09:47:00
# @Last Modified time: 2018-05-04 14:27:58

import asyncio
import orm
from models import User

@asyncio.coroutine
def create_user():
    yield from orm.create_pool(loop=loop,user='',password='',db='awesome')

    u = User(name='',email='admin@example.com',passwd='',admin=,image='about:blank')

    yield from u.save()

loop = asyncio.get_event_loop()
loop.run_until_complete(create_user())
loop.run_forever()
