#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: xie
# @Date:   2018-06-02 17:06:51
# @Last Modified time: 2018-06-20 15:59:39
from flask import render_template,request,make_response,redirect,url_for,abort,send_from_directory
from app import app,db
import os,logging,hashlib,json,time
from models import Users,News,Others
from wtforms import StringField,SubmitField
from flask_ckeditor import CKEditor,CKEditorField,upload_fail,upload_success
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired

logging.basicConfig(level=logging.INFO)
is_logined=False

ckeditor=CKEditor(app)
app.config['UPLOADED_PATH'] = os.path.join(os.path.dirname(__file__), 'uploads')

class Forms_new(FlaskForm):
    title=StringField('标题:',validators=[DataRequired()])
    body=CKEditorField('正文:',validators=[DataRequired()])
    submit=SubmitField('保存')

@app.route('/manage/news/create',methods=['GET','POST'])
def create_new():
    form=Forms_new()
    errer=None
    if form.validate_on_submit():
        title=form.title.data.rstrip().encode('utf-8')
        body=form.body.data.rstrip().encode('utf-8')
        if not title or not body:
            errer="标题、正文都不能为空!"
            return render_template('news_create.html',err=errer,form=form)
        t=str(int(time.time()))
        new=News(name=title,content=body,created_at=t)
        db.session.add(new)
        db.session.commit()
        errer='保存成功!'
        return render_template('news_create.html',err=errer,form=form)
    return render_template('news_create.html',form=form,err=errer)

@app.route('/manage/news/edit/<new_id>',methods=['GET','POST'])
def edit_new(new_id):
    errer=None
    logging.info('edit new :%s'%new_id)
    form=Forms_new()
    new=News.query.filter_by(id=new_id).first()
    if request.method=='GET':
        form.title.data=new.name
        form.body.data=new.content 
        return render_template('news_edit.html',err=errer,form=form)
    if form.validate_on_submit():
        title=form.title.data.rstrip().encode('utf-8')
        body=form.body.data.rstrip().encode('utf-8')     
        if not title or not body:
            errer="标题、正文都不能为空!"
            return render_template('news_edit.html',err=errer,form=form)
        re=News.query.filter_by(id=new_id).update({'name':title,'content':body})
        db.session.commit()
        if re:
            errer='保存成功!'
            return render_template('news_edit.html',form=form,err=errer)

@app.route('/manage/others/add',methods=['GET','POST'])
def add_other():
    global is_logined
    if is_logined:
        errer=None
        form=Forms_new()
        if request.method=='GET':
            return render_template('others_add.html',err=errer,form=form)
        if form.validate_on_submit():
            title=form.title.data.rstrip().encode('utf-8')
            body=form.body.data.rstrip().encode('utf-8')
            print('other title:%s,body:%s'%(title,body))     
            if not title or not body:
                errer="标题、正文都不能为空!"
                return render_template('others_add.html',err=errer,form=form)
            other=Others(name=title,content=body)
            logging.info('add other:%s,%s'%(other.name,other.content))
            db.session.add(other)
            db.session.commit()
            errer='保存成功!'
            return render_template('others_add.html',err=errer,form=form)
    else:
        return redirect(url_for('login'))

@app.route('/manage/others/edit/<other_id>',methods=['GET','POST'])
def edit_other(other_id):
    errer=None
    form=Forms_new()
    logging.info('edit other :%s'%other_id)
    other=Others.query.filter_by(id=other_id).first()
    if request.method=='GET':
        form.title.data=other.name
        form.body.data=other.content 
        return render_template('others_edit.html',err=errer,form=form)
    if form.validate_on_submit():
        title=form.title.data.rstrip().encode('utf-8')
        body=form.body.data.rstrip().encode('utf-8')     
        if not title or not body:
            errer="标题、正文都不能为空!"
            return render_template('others_edit.html',err=errer,form=form)
        re=Others.query.filter_by(id=other_id).update({'name':title,'content':body})
        db.session.commit()
        if re:
            errer='保存成功!'
            return render_template('others_edit.html',form=form,err=errer)

@app.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('upload')
    extension = f.filename.split('.')[1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg']:
        return upload_fail(message='只能上传图片!')
    f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
    url = url_for('uploaded_files', filename=f.filename)
    return upload_success(url=url)

@app.route('/files/<filename>')
def uploaded_files(filename):
    path = app.config['UPLOADED_PATH']
    return send_from_directory(path, filename)
           
def check_admin():
    global is_logined
    if request.cookies is None:
        is_logined=False
    else: 
        cookie=request.cookies.get('awesome')
        if not cookie:
            is_logined=False
        is_logined = cookie2user(cookie)

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/templates/project_intro.html/<page>')
def project_intro(page):
    news=News.query.all()
    news_count=len(news)
    #page='1'
    index=page_str2int(page)
    p=Page(news_count,index,page_size=15)
    n=news[p.offset:p.offset+p.limit]
    others=Others.query.all()
    return render_template('project_intro.html',news=n,page=p,others=others)

@app.route('/templates/login.html',methods=['GET'])
def login():
    errer=None
    if request.method == 'GET':
        return render_template('login.html',err=errer)

@app.route('/api/signout')
def signout():
    r=make_response(render_template('login.html'))
    r.set_cookie(app.config['COOKIE_NAME'],'',max_age=0,httponly=True)
    logging.info('signout')
    return r

@app.route('/templates/admin',methods=['GET','POST'])
def admin():
    errer=None
    global is_logined
    logging.info('is_logined:%d'%is_logined)  
    news=News.query.all()
    news_count=len(news)
    page='1'
    index=page_str2int(page)
    page=Page(news_count,index)
    n=news[page.offset:page.offset+page.limit]
    #GET
    if request.method=='GET':
        check_admin()
        if is_logined:
            return render_template('admin.html',news=n,page=page)
        else:
            abort(403)
    else:
        form=request.form
        name=form['name']
        passwd=form['passwd']
        logging.info('check user: %s,%s'%(name,passwd))
        if not name or not passwd:
            errer="用户名、密码不能为空"
            return render_template('login.html',err=errer)
        user = Users.query.filter_by(name=name).first()
        if user is None:
            errer='用户不存在'
            return render_template('login.html',err=errer)
        #user=users[0]
        #检查密码
        if passwd != user.passwd:
            errer='密码无效'
            return render_template('login.html',err=errer)
        is_logined=True
        logging.info('login user : %s'%user)
        r = make_response(render_template('admin.html',news=n,page=page))
        r.set_cookie(app.config['COOKIE_NAME'],user2cookie(user,86400),max_age=86400,httponly=True)
        return r

@app.route('/templates/admin/<page>')
def gotopg(page):
    news=News.query.all()
    news_count=len(news)
    index=page_str2int(page)
    page=Page(news_count,index)
    if news_count==0:
        return render_template('admin.html',news=None,page=page)
    #n=News.query.paginate(page.page_index,)
    n=news[page.offset:page.offset+page.limit]
    return render_template('admin.html',news=n,page=page)

@app.route('/api/news/<id>')
def get_new(id):
    new=News.query.filter_by(id=id).first()
    return render_template('new.html',new=new)

def user2cookie(user,max_age):
    expires=str(int(time.time()+max_age))
    check_str='%s-%s-%s-%s'%(user.id,user.passwd,expires,app.config['SECRET_KEY'])
    l=[user.id,expires,hashlib.sha1(check_str.encode('utf-8')).hexdigest()]
    return '-'.join(l)

def cookie2user(cookie):
    if not cookie:
        return False
    l=cookie.split('-')
    if len(l) != 3:
        return False
    uid,expires,sha1=l
    if int(expires) < time.time():
        return False
    user=Users.query.filter_by(id=uid).first()
    if user is False:
        return False
    s='%s-%s-%s-%s'%(user.id,user.passwd,expires,app.config['SECRET_KEY'])
    if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
        logging.info('invalid sha1 for cookie check.')
        return False
    else:
        return True

@app.route('/manage/news/delete',methods=['GET','POST'])
def delete_new():
    global is_logined
    if is_logined:
        new_id=request.args.get('id',None)
        logging.info('delete new :%s'%(new_id))
        new=News.query.filter_by(id=new_id).first()
        if new is None:
            abort(400)
        db.session.delete(new)
        db.session.commit()
        return 'ok'
    else:
        return redirect(url_for('login'))

@app.route('/manage/others')
def others():
    global is_logined
    if is_logined:
        others=Others.query.all()
        logging.info('others type:%s --> %s'%(type(others),others))        
        return render_template('others.html',others=others)
    else:
        return redirect(url_for('login'))   

@app.route('/manage/others/delete',methods=['GET','POST'])
def delete_other():
    global is_logined
    if is_logined:
        id=request.args.get('id',None)
        logging.info('delete other :%s'%(id))
        other=Others.query.filter_by(id=id).first()
        if other is None:
            abort(400)
        db.session.delete(other)
        db.session.commit()
        return 'ok'
    else:
        return redirect(url_for('login'))