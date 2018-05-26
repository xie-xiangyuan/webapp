#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: xie
# @Date:   2018-04-09 16:10:40
# @Last Modified time: 2018-05-22 16:47:49

import asyncio,hashlib,time,json,logging
from models import User,News,Others     
from coroweb import get,post
from aiohttp import web
from apis import APIValueError,APIPermissionError

logging.basicConfig(level=logging.INFO)

COOKIE_NAME='awesome'
_COOKIE_KEY='awesome'

def check_admin(request):
    if request.__user__ is None or not request.__user__['admin']:
        return None
    return True

class Page(object):
    def __init__(self,item_count,page_index=1,page_size=10):
        self.item_count=item_count
        self.page_size=page_size
        self.page_count=item_count // page_size + (1 if item_count % page_size >0 else 0)
        if (self.item_count == 0) or (page_index>self.page_count):
            self.page_index=1
            self.offset=0
            self.limit=0
        else:
            self.page_index=page_index
            self.offset=self.page_size*(page_index-1)
            self.limit=self.page_size
        self.has_next=self.page_index<self.page_count
        self.has_previous=self.page_index>1

def page_str2int(page_str):
    p=1
    try:
        p=int(page_str)
    except:
        pass
    if p<1:
        p=1
    return p    

@get('/')
async def index(request):
    return {'__template__':'index.html'}

@get('/templates/project_intro.html')
async def project_intro(request,*,page='1'):
    page_index=page_str2int(page)
    news_num=await News.findNumber('count(id)')
    pg=Page(news_num,page_index,page_size=20)
    news=await News.findAll(orderBy='created_at desc',limit=(pg.offset,pg.limit))
    others=await Others.findAll()
    return {'__template__':'project_intro.html','news':news,'page':pg,'others':others}

@get('/api/news/')
async def show_new(request,*,id):
     n=await News.find(id)
     return {'__template__':'new.html','new':n}

@get('/templates/login.html')
async def login(request):
    return {'__template__':'login.html'}

@get('/templates/admin.html')
async def admin(request,*,page='1'):
    re=check_admin(request)
    if re is None:
        return {'__template__':'login.html'}
    page_index=page_str2int(page)
    news_num=await News.findNumber('count(id)')
    pg=Page(news_num,page_index)
    if news_num==0:
        return {'__template__':'admin.html','page':pg,'news':''}
    n=await News.findAll(orderBy='created_at desc',limit=(pg.offset,pg.limit))
    return {'__template__':'admin.html','page':pg,'news':n}

@post('/manage/news/delete')
async def delete_new(request,*,id):
    re=check_admin(request)
    if re is None:
        return {'__template__':'login.html'}
    n=await News.find(id)
    await n.remove()
    return dict(id=id)

@get('/manage/news/edit')   #获取编辑页面
async def new_edit(request,*,id):
    re=check_admin(request)
    if re is None:
        return {'__template__':'login.html'}
    n=await News.find(id)
    return {'__template__':'news_edit.html','new':n}

@post('/manage/edit/new')   #保存编辑页面
async def edit_new(request,*,id,name,summary,content):
    re=check_admin(request)
    if re is None:
        return {'__template__':'login.html'}
    n=await News.find(id)
    n.name=name.strip().encode('utf-8')
    n.summary=summary.strip().encode('utf-8')
    n.content=content.rstrip().encode('utf-8')
    await n.update()
    return str(n)

@get('/manage/news/create')
async def news_create(request):
    re=check_admin(request)
    if re is None:
        return {'__template__':'login.html'}
    return {'__template__':'news_create.html'}

@post('/manage/create/new')
async def create_new(request,*,name,summary,content):
    re=check_admin(request)
    if re is None:
        return {'__template__':'login.html'}
    if not name:
        raise APIValueError('name','name cannot be empty')
    if not summary:
        raise APIValueError('summary','summary cannot be empty')    
    if not content:
        raise APIValueError('content','content cannot be empty')
    new=News(user_id=request.__user__.id,user_name=request.__user__.name,user_image=request.__user__.image,name=name.strip().encode('utf-8'),summary=summary.strip().encode('utf-8'),content=content.rstrip().encode('utf-8'))
    r=await new.save()
    return str(r)

@get('/manage/others')
async def others(request):
    re=check_admin(request)
    if re is None:
        return {'__template__':'login.html'}
    others=await Others.findAll()
    return {'__template__':'others.html','others':others}

@get('/manage/others/add')
async def others_add(request):
    return {'__template__':'others_add.html'}

@post('/manage/others/create')
async def others_create(request,*,name,content):
    re=check_admin(request)
    if re is None:
        return {'__template__':'login.html'}
    if not name:
        raise APIValueError('name','name cannot be empty')
    if not content:
        raise APIValueError('content','content cannot be empty')
    o=Others(image='_blank'.encode('utf-8'),name=name.strip().encode('utf-8'),summary='_blank'.encode('utf-8'),content=content.rstrip().encode('utf-8'))
    await o.save()
    return str(o)

@post('/manage/others/delete')
async def delete_others(request,*,id):
    re=check_admin(request)
    if re is None:
        return {'__template__':'login.html'}
    o=await Others.find(id)
    await o.remove()
    return dict(id=id)

@get('/manage/others/edit')
async def others_edit(request,*,id):
    re=check_admin(request)
    if re is None:
        return {'__template__':'login.html'}
    o=await Others.find(id)
    return {'__template__':'others_edit.html','other':o}

@post('/manage/edit/other')
async def edit_other(request,*,id,name,content):
    re=check_admin(request)
    if re is None:
        return {'__template__':'login.html'}
    o=await Others.find(id)
    o.name=name.strip().encode('utf-8')
    o.content=content.rstrip().encode('utf-8')
    await o.update()
    return str(o)

@get('/api/signout')
async def signout(request):
    referer=request.headers.get('Referer')
    r=web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME,'',max_age=0,httponly=True)
    logging.info('signout user:%s  ; Referer:%s'%(request.__user__,referer))
    return r

@post('/api/authenticate')
async def auth(request,*,name,passwd):
    if not name:
        raise APIValueError('name','invalid name.')
    if not passwd:
        raise APIValueError('passwd','invalid passwd.')
    users = await User.findAll('name=?',[name])
    if len(users)==0:
        raise APIValueError('name','name not exists.')
    user=users[0]
    #检查密码
    sha1=hashlib.sha1()
    sha1.update(user.name.encode('utf-8'))
    sha1.update(b':')
    sha1.update(user.passwd.encode('utf-8'))
    if passwd != sha1.hexdigest():
        raise APIValueError('passwd','invalid passwd.')
    logging.info('login user : %s'%user)
    #通过认证
    r = web.Response()
    r.set_cookie(COOKIE_NAME,user2cookie(user,86400),max_age=86400,httponly=True)
    r.content_type='application/json'
    user.passwd='******'
    r.body=json.dumps(user,ensure_ascii=False).encode('utf-8')
    return r

def user2cookie(user,max_age):
    expires=str(int(time.time()+max_age))
    check_str='%s-%s-%s-%s'%(user.id,user.passwd,expires,_COOKIE_KEY)
    l=[user.id,expires,hashlib.sha1(check_str.encode('utf-8')).hexdigest()]
    return '-'.join(l)

async def cookie2user(cookie_name):
    if not cookie_name:
        return None
    L=cookie_name.split('-')
    if len(L) != 3:
        return None
    uid,expires,sha1=L
    if int(expires)<time.time():
        return None
    user=await User.findAll('id=?',[uid])
    if user is None:
        return None
    u=user[0]
    s='%s-%s-%s-%s'%(uid,u.passwd,expires,_COOKIE_KEY)
    if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
        logging.info('invalid sha1 for cookie check...')
        return None
    return u
