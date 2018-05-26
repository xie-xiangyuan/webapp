import aiomysql , logging , asyncio

logging.basicConfig(level=logging.NOTSET)

async def create_pool(**kw):
    logging.info("creating global db connection pool......")
    global __pool
    __pool = await aiomysql.create_pool(
        host = kw.get('host','localhost'),
        port = kw.get('port',3306),
        user = kw['user'],
        password = kw['password'],
        db=kw['db'],
        charset=kw.get('charset', 'utf8'),
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        loop=kw['loop']
        )

async def select(sql,args,size=None):
    logging.info("SQL:%s %s"%(sql,args))
    global __pool
    async with __pool.get() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql.replace('?','%s'),args or ())
            if size:
                rs = await cur.fetchmany(size) 
            else: 
                rs = await cur.fetchall()  
        logging.info("rows returned:%s"%len(rs))
        return rs

async def execute(sql,args,autocommit=True):
    logging.info("SQL:%s %s"%(sql,args))
    global __pool
    async with __pool.get() as conn:
        if not autocommit:
            await conn.begin()

        async with conn.cursor(aiomysql.DictCursor) as cur:
            print('sql:%s,args:%s'%(sql,args))
            await cur.execute(sql.replace('?','%s'),args)
            #await conn.commit()
            affected = cur.rowcount
        if not autocommit:
            await conn.commit()
        return affected

        ''' 
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql.replace('?','%s'),args or ())
                affected = cur.rowcount
            if not autocommit:
                await conn.commit()
            return affected     
        except BaseException as e:
             if not autocommit:
                await conn.rollback()
             raise   
        #return affected    '''    

def create_str_args(num):
    L=[]
    for n in range(num):
        L.append('?')
    return ','.join(L)   

class field(object):
    def __init__(self,field_name,field_type,is_primarykey,default):
        self.field_name = field_name
        self.field_type = field_type
        self.is_primarykey = is_primarykey
        self.default = default

    def __str__(self):
            return '<class:%s,%s,%s >'%(self.__class__.__name__,self.field_name,self.field_type)

class int_field(field):
    def __init__(self,field_name=None,is_primarykey=False,default=0):
        super().__init__(field_name,'bigint',is_primarykey,default)

class bool_field(field):
    def __init__(self,field_name=None,default=False):
        super().__init__(field_name,'boolean',False,default)

class str_field(field):
    def __init__(self,field_name=None,is_primarykey=False,default=None,ddl='varchar(100)'):
        super().__init__(field_name,ddl,is_primarykey,default)

class float_field(field):
    def __init__(self,field_name=None,is_primarykey=False,default=0.0):
        super().__init__(field_name,'real',is_primarykey,default)     

class text_field(field):
    def __init__(self,field_name=None,is_primarykey=False,default=None):
        super().__init__(field_name,'text',is_primarykey,default)                           

class ModelMetaclass(type):
    def __new__(cls,name,bases,attrs):
        if name == "Model":
            return type.__new__(cls,name,bases,attrs)
        tableName = attrs.get('__table__',None) or name
        logging.info('found Model:%s ,table:%s'%(name,tableName))
        mappings = dict()
        primary_key=None
        fields=[]
        for k,v  in attrs.items():
            if isinstance(v,field):
                logging.info('found mapping:%s--%s'%(k,v))
                mappings[k]=v
                if v.is_primarykey:
                    if primary_key:
                        raise StandardError('Duplicate primary key for field: %s' % k)
                    primary_key=k
                else:
                    fields.append(k)           
        if not primary_key:
            raise StandardError('primary key not found')
        for k in mappings.keys():
            attrs.pop(k)
        list_fields=list(map(lambda f:'`%s`'%f,fields))
        print('-----mappings--%s'%mappings)
        attrs['__mappings__']=mappings
        attrs['__tableName__']=tableName
        attrs['__fields__']=fields
        attrs['__primary_key__']=primary_key
        attrs['__select__']='select `%s`,%s from %s '%(primary_key,','.join(list_fields),tableName) 
        attrs['__insert__']='insert into %s (%s,`%s`) values (%s)'%(tableName,','.join(list_fields),primary_key,create_str_args(len(list_fields)+1))
        attrs['__update__']="update %s set %s where `%s` = ?"%(tableName,','.join(map(lambda f:'`%s`=?'%f,fields)),primary_key)
        attrs['__delete__']='delete from %s where `%s`=?'%(tableName,primary_key)
        return type.__new__(cls,name,bases,attrs)

class Model(dict,metaclass=ModelMetaclass):
    '''__metaclass__ = ModelMetaclass'''

    def __init__(self,**kw):
        super(Model,self).__init__(**kw)
     
    def __getattr__(self,key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError('Model has no attribute %s'%key)    

    def __setattr__(self,key,value):
        self[key]=value

    def getValue(self,key):
        return getattr(self,key,None)

    def getValueOrDefault(self,key):
        value = getattr(self,key,None)
        if value is None:
            field = self.__mappings__[key]
            #print('@@@@@field:%s'%field)
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('use default value for %s--%s'%(key,str(value)))
                setattr(self,key,value)
        return value

    @classmethod
    async def findAll(cls,where=None,args=None,**kw):
        sql=[cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args=[]
        orderBy=kw.get('orderBy',None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)
        limit=kw.get('limit',None)
        if limit:
            sql.append('limit')
            if isinstance(limit,int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit,tuple) and len(limit)==2:
                sql.append('?,?')
                args.extend(limit)
            else:
                raise ValueError('invalid limit value.')
        rs=await select(' '.join(sql),args)
        return [cls(**r) for r in rs]

    @classmethod
    async def findNumber(cls,field,where=None,args=None):
        sql=['select %s _num_ from %s'%(field,cls.__tableName__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs = await select(' '.join(sql),args,1)
        if len(rs) == 0:
            return None
        print('----rs:%s in findNumber'%rs)
        return rs[0]['_num_']

    @classmethod
    async def find(cls,pk):
        sql='%s where `%s` =? '%(cls.__select__,cls.__primary_key__)
        rs = await select(sql,pk,1)
        if len(rs) == 0:
            return None
        return  cls(**rs[0])

    async def save(self):
        sql=self.__insert__
        print('-----_fileds_:%s'%self.__fields__)
        args=list(map(self.getValueOrDefault,self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        print('------args:%s'%args)
        ret_rows=await execute(sql,args)
        if ret_rows != 1:
            logging.warn('failed to insert record :affected rows %s'%ret_rows)


    async def update(self):
        args = list(map(self.getValue, self.__fields__))
        args.append(self.getValue(self.__primary_key__))
        ret_rows = await execute(self.__update__, args)
        if ret_rows != 1:
            logging.warn('failed to update by primary key: affected rows: %s' % ret_rows)

    async def remove(self):
        args=[self.getValue(self.__primary_key__)]
        ret_rows = await execute(self.__delete__,args)
        if ret_rows != 1:
            logging.warn('failed to remove by primary key: affected rows: %s' % ret_rows)




