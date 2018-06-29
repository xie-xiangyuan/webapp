#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: xie
# @Date:   2018-06-02 17:03:28
# @Last Modified time: 2018-06-19 17:05:04

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@localhost:3306/flaskapp?charset=utf8'
SQLALCHEMY_TRACK_MODIFICATIONS = True
CSRF_ENABLED = True
COOKIE_NAME='awesome'
SECRET_KEY='awesome-admin-123'
CKEDITOR_SERVE_LOCAL = True
CKEDITOR_HEIGHT = 400 
CKEDITOR_FILE_UPLOADER = 'upload'
