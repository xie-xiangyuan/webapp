#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: xie
# @Date:   2018-06-26 11:33:38
# @Last Modified time: 2018-06-29 10:45:00

import unittest
import app

class FlaskappTestCase(unittest.TestCase):

    def setUp(self):
        app.app.config['TESTING']=True
        self.app_client=app.app.test_client()
        self.db=app.db

    def tearDown(self):
        pass

    def test_index(self):
        rc=self.app_client.get('/')
        print('rc-type:%s,rc:%s'%(type(rc),rc))
        assert '首页' in rc.data.decode()

    def test_project_intro(self):
        #rc=self.app_client.get(url_for('project_intro',page=1))
        rc=self.app_client.get('/templates/project_intro.html/1')
        assert '项目概况' in rc.data.decode()
        assert '专家团队' in rc.data.decode()
        assert '会员权益' in rc.data.decode()

    def test_login_post(self):
        rc=self.login(' ','admin')
        assert 'Error:' in rc.data.decode()
        rc=self.login('admin',' ')
        assert 'Error:' in rc.data.decode()
        rc=self.login('admin','admin')
        assert '密码无效' in rc.data.decode()
        rc=self.login('xie','admin')
        assert '用户不存在' in rc.data.decode()
        rc=self.login('admin','admin@123')
        assert '新闻列表' not in rc.data.decode()
        with self.app_client as c:
            rc=c.post('/templates/admin',data=dict(name='admin',passwd='admin@123'),follow_redirects=True)
            assert request.form['name'] == 'admin'
            assert request.form['passwd'] == 'admin@123'
        #print('cookie:%s'%rc.cookie)
        #assert self.assert_equal(rc.cookie['awesome'],app.config['COOKIE_NAME'])

    def login(self,name,passwd):
        return self.app_client.post('/templates/admin',data=dict(name=name,passwd=passwd),follow_redirects=True)

    def test_login_get(self):
        rc=self.app_client.get('/templates/admin')
        assert 'Forbidden' in rc.data.decode()

    def test_logout(self):
        rc=self.app_client.get('/api/signout', follow_redirects=True)
        assert '管理员登录' in rc.data.decode()

    def test_upload(self):
        with self.app_client as c:
            rc=c.post('/upload',data=dict(upload='111.png'))
            print('rc-type:%s,rc:%s'%(type(rc),rc))
            assert request.files.get('upload') is None

    def test_uploaded_files(self):
        rc=self.app_client.get('/files/111.png')
        assert 'Not Found' in rc.data.decode()
        rc=self.app_client.get('/files/hy2.png')
        print('rc-type:%s,rc:%s'%(type(rc),rc))
        assert '200 ok' in rc.data.decode()

    def test_manage_others(self):
        rc=self.app_client.get('/manage/others/add', follow_redirects=True)
        assert '管理员登录' in rc.data.decode()
        rc=self.app_client.get('/manage/others/edit')
        assert 'Not Found' in rc.data.decode()
        rc=self.app_client.get('/manage/others/delete', follow_redirects=True)
        assert '管理员登录' in rc.data.decode()

    def test_manage_news(self):
        rc=self.app_client.get('/manage/news/create', follow_redirects=True)
        assert '正文' in rc.data.decode()
        rc=self.app_client.get('/manage/news/edit')
        assert 'Not Found' in rc.data.decode()
        rc=self.app_client.get('/manage/news/delete', follow_redirects=True)
        assert '管理员登录' in rc.data.decode()

if __name__=='__main__':
    unittest.main()
