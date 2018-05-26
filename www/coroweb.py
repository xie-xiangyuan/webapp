#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: xie
# @Date:   2018-04-09 16:16:05
# @Last Modified time: 2018-05-05 15:44:16

import asyncio,inspect,logging,functools
from aiohttp import web
from urllib import parse
from apis import APIError

logging.basicConfig(level=logging.NOTSET)

def get(path):
    def decorator(func):
        @functools.wraps(func)    #将wrapper函数改名为func
        def wrapper(*args,**kw):
            return func(*args,**kw)
        wrapper.__method__='GET'
        wrapper.__route__=path
        return wrapper    
    return decorator       

def post(path):
    def decorator(func):
        @functools.wraps(func)    #将wrapper函数改名为func
        def wrapper(*args,**kw):
            return func(*args,**kw)
        wrapper.__method__='POST'
        wrapper.__route__=path
        return wrapper    
    return decorator

def add_routes(app,module_name):
    n=module_name.rfind('.')
    if n==-1:
        module=__import__(module_name)
        print('-------module1:%s'%module)
    else:
        name=module_name[n+1:]
        module=getattr(__import__(module_name[:n]),name)
        print('-------module2:%s'%module)
    for attr in dir(module):
        if attr.startswith('_'):
            continue
        fn=getattr(module,attr)
        if callable(fn):
            method=getattr(fn,'__method__',None)
            path=getattr(fn,'__route__',None)
            if method and path:
                add_route(app,fn)

def add_route(app,fn):
    method=getattr(fn,'__method__',None)
    path=getattr(fn,'__route__',None)
    if  method is None or path is None:
        raise ValueError('method or path not defined of %s'%str(fn))
    if not asyncio.iscoroutinefunction(fn) and inspect.isgeneratorfunction(fn):
        fn=asyncio.coroutine(fn)
    logging.info('add route %s,%s-->%s(%s)'%(method,path,fn.__name__,','.join(inspect.signature(fn).parameters.keys())))
    app.router.add_route(method,path,RequestHandler(app,fn))

def get_required_kw_args(fn):
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
            args.append(name)
    return tuple(args)

def get_named_kw_args(fn):
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
    return tuple(args)

def has_named_kw_args(fn):
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            return True

def has_var_kw_arg(fn):
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True

def has_request_arg(fn):
    found=False
    sig=inspect.signature(fn)
    params=sig.parameters
    for name,param in params.items():
        if name=='request':
            found=True
            continue
        if found and (param.kind != inspect.Parameter.VAR_POSITIONAL and  param.kind != inspect.Parameter.KEYWORD_ONLY and param.kind != inspect.Parameter.VAR_KEYWORD):    
            raise ValueError('request parameter must be the last named parameter for function:%s%s'%(fn,__name__,str(sig)))
        return found


class RequestHandler(object):
    def __init__(self,app,fn):
        self._app=app
        self._func=fn
        self._has_request_arg=has_request_arg(fn)
        self._has_var_kw_arg=has_var_kw_arg(fn)
        self._has_named_kw_args = has_named_kw_args(fn)
        self._named_kw_args = get_named_kw_args(fn)
        self._required_kw_args = get_required_kw_args(fn)

    async def __call__(self,request):
        kw=None
        print('------request handler:%s in %s'%(request,self._func.__name__))
        if self._has_var_kw_arg or self._has_named_kw_args or self._required_kw_args:
            if request.method=='POST':
                if not request.content_type:
                    return web.HTTPBadRequest('no content_type')
                ct=request.content_type.lower()        
                if ct.startswith('application/json'):
                    params=await request.json()
                    if not isinstance(params,dict):
                        return web.HTTPBadRequest('POST request params not a dict ')
                    kw=params
                elif ct.startswith('application/x-www-form-urlencoded') or ct.startswith('multipart/form-data'):
                    params=await request.post()
                    kw=dict(**params)
                else:
                    return web.HTTPBadRequest('not supported content_type:%s'%request.content_type)
            if request.method=='GET':
                qs=request.query_string
                if qs:
                    kw=dict()
                    for k,v in parse.parse_qs(qs,True).items():
                        kw[k]=v[0]
        if kw is None:
            kw=dict(**request.match_info)
        else:
            if not self._has_var_kw_arg and self._named_kw_args:
                copy=dict()
                for name in self._named_kw_args:
                    if name in kw:
                        copy[name]=kw[name]
                kw=copy
            for k, v in request.match_info.items():
                if k in kw:
                    logging.warning('Duplicate arg name in named arg and kw args: %s' % k)
                kw[k] = v
        #if self._has_request_arg:
        #    kw['request']=request
        if self._required_kw_args:
            for name in self._required_kw_args:
                if name not in kw:
                    return web.HTTPBadRequest('missed arg: %s'%name)
        logging.info('call with args:%s'%str(kw))
        try:
            logging.info('******args passed to URL handler : %s'%str(kw))
            re=await self._func(request,**kw)
            return re
        except APIError as e:
            return dict(error=e.error, data=e.data, message=e.message)
















