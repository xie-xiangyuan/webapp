#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: xie
# @Date:   2018-04-09 16:27:51
# @Last Modified time: 2018-05-23 17:06:18

import asyncio,orm
from aiohttp import web
from coroweb import add_routes
import logging,json,os,time
from jinja2 import Environment,FileSystemLoader
from handlers import COOKIE_NAME, cookie2user
from config import configs
logging.basicConfig(level=logging.INFO)

'''
#for test
def index(request):
    return web.Response(body=b'<h1>hello</h1>')
'''

def init_jinjia2(app,**kw):
    logging.info('init jinja2...')
    options=dict(
        autoescape=kw.get('autoescape',True),
        block_start_string=kw.get('block_start_string','{%'),
        block_end_string=kw.get('block_end_string','%}'),
        variable_start_string=kw.get('variable_start_string','{{'),
        variable_end_string=kw.get('variable_end_string','}}'),
        auto_reload=kw.get('auto_reload',True)
        )
    path=kw.get('path',None)
    if path is None:
        path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'templates')
    logging.info('set templates path...')
    env=Environment(loader=FileSystemLoader(path),**options)
    filters=kw.get('filters',None)
    if filters is not None:
        for k,v in filters.items():
            env.filters[k]=v
    app['__templating__']=env


async def response_factory(app,handler):    #此handler为coroweb.RequestHandler的实例（此函数由框架调用，传入参数）
    async def response(request):    #reqeust 是aiohttp框架Request类的提供的全局唯一实例（单例模式），存储客户端所有请求相关数据
        logging.info('response handler...')
        re = await handler(request)
        if isinstance(re,web.StreamResponse):
            print('-----in StreamResponse-----')
            return re
        if isinstance(re,bytes):
            resp=web.Response(body=re)
            resp.content_type='application/octet-stream'
            return resp
        if isinstance(re,str):
            if re.startswith('redirect:'):
                return web.HTTPFound(re[9:])
            resp=web.Response(body=re.encode('utf-8'))
            resp.content_type='text/html;charset=utf-8'
            return resp
        '''
        if isinstance(re,dict):
            print('-----in dict response-------')
            template=re['__template__']
            if template is None:
                resp=web.Response(body=json.dumps(re,  ensure_ascii=False,default=lambda o: o.__dict__).encode('utf-8'))
                resp.content_type='application/josn;charset=utf-8'
                return resp
            else:
                resp=web.Response(body=app['__templating__'].get_template(template).render(**re).encode('utf-8'))
                resp.content_type='text/html;charset=utf-8'
                return resp
        '''
        if isinstance(re,dict):
            print('------in dict response')
            try:
                logging.info('in text/html response1')
                template=re['__template__']
            except Exception as e:
                logging.info('in json response')
                resp=web.Response(body=json.dumps(re,  ensure_ascii=False,default=lambda o: o.__dict__).encode('utf-8'))
                resp.content_type='application/josn;charset=utf-8'
                return resp
            else:
                    try:
                        resp=web.Response(body=app['__templating__'].get_template(template).render(**re).encode('utf-8'))
                        resp.content_type='text/html;charset=utf-8'
                        logging.info('in text/html response2 with data.')
                        return resp
                    except:
                        resp=web.Response(body=app['__templating__'].get_template(template).render(**re).encode('utf-8'))
                        logging.info('in text/html response3 wisth no data')
                        return resp
            finally:
                pass

        if isinstance(re,int):
            if re<600 and re>=100:
                return web.Response(r)
        if isinstance(re,tuple) and len(re)==2:
            t,m=re
            if isinstance(t,int) and t>=100 and t<600:
                return web.Response(t,str(m))
        #default
        resp=web.Response(body=str(re).encode('utf-8'))
        resp.content_type='text/plain;charset=utf-8'
        return resp
    return response   

async def auth_factory(app,handler):
    async def auth(request):
        logging.info('check user:%s %s'%(request.method,request.path))
        request.__user__=None
        cookie_name=request.cookies.get(COOKIE_NAME)    #从request获取cookie
        if cookie_name:
            #print('----cookie name:%s----'%cookie_name)
            user=await cookie2user(cookie_name)     #解密cookie
            if user:
                logging.info('set current user:%s'%user)
                request.__user__=user    #将有效用户绑定到request
        return (await handler(request))
    return auth    


def add_static(app):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    app.router.add_static('/static/', path)
    logging.info('add static %s => %s' % ('/static/', path))

def datetime_filter(t):
    delta=int(time.time()-t)
    if delta < 60:
        return '1分钟前'
    if delta < 60*60:
        return '%s分钟前'%(delta//60)
    if delta < 3600*24:
        return '%s小时前'%(delta//3600)
    if delta < 3600*24*7:
        return '%s天前'%(delta//(3600*24))
    dt=time.localtime(t)
    return '%s年%s月%s日'%(dt.tm_year,dt.tm_mon,dt.tm_mday)

async def init(loop):
    #await orm.create_pool(loop=loop, host='127.0.0.1', port=3306, user='root', password='password', db='awesome')
    await orm.create_pool(loop=loop,**configs['db']) 
    app=web.Application(loop=loop,middlewares=[auth_factory,response_factory])
    #app.router.add_route('GET','/',index)
    init_jinjia2(app,filters=dict(datetime=datetime_filter))
    add_routes(app,'handlers')
    add_static(app)
    server=await loop.create_server(app.make_handler(),'192.168.101.241',9000)
    return server

loop=asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
