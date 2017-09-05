#单例测试导入路径
if __name__ == '__main__':
    import sys, os
    parent_path = os.path.dirname(os.getcwd())
    sys.path.append(parent_path)

import pymysql, re, socket, time, os
from pymysql.cursors import Cursor
from DBUtils.PooledDB import PooledDB

from log.logger import LOG
from config import CF


global HOSTIP,PID
HOSTIP = str(socket.gethostbyname(socket.gethostname()))
PID = str(os.getpid())

#数据库工具类
class MySqlEx():
    __pool = None
    #__con = None
    __re = re.compile(r'\s')

    @classmethod
    def getConn(cls):
        if cls.__pool is None:
            cls.__pool = PooledDB(host=CF.get('db', 'host'),
                                  port=CF.getint('db', 'port'),
                                  db=CF.get('db', 'db'),
                                  user=CF.get('db', 'user'),
                                  passwd=CF.get('db', 'passwd'),
                                  creator=pymysql,
                                  #maxusage=0,
                                  mincached=1,
                                  maxcached=1,
                                  maxconnections=1,
                                  blocking=True,
                                  use_unicode=True,
                                  charset='utf8',
                                  cursorclass=Cursor)

        # cls.__con = pymysql.connect(host=CF.get('db', 'host'),
        #                             port=CF.getint('db', 'port'),
        #                             db=CF.get('db', 'db'),
        #                             user=CF.get('db', 'user'),
        #                             passwd=CF.get('db', 'passwd'),
        #                             charset='utf8')
            LOG.info('创建%s主机%s数据库连接池成功!', CF.get('db', 'host'), CF.get('db', 'db'))
        #LOG.info('打开cursor成功!')
        return cls.__pool.connection()

    def __openclose(f):
        def fn(*args, **kw):
            # try:
            #     if MySqlEx.__con is None:
            #         MySqlEx.getConn(CF)
            # except Exception as e:
            #     LOG.error('连接mysql出错,错误信息:%s', str(e))
            t1 = time.time()
            fr = f(*args, **kw)
            t2 = time.time()
            LOG.info('存储数据耗时:%f' % (t2-t1))
            return fr
        return fn

    @classmethod
    @__openclose
    def save(cls, obj, metadatas, autocommit=True):
        #将信息转换成SQL语句
        try:
            save_sql = 'insert into t_esf (%s) values ("%s","%s","%s")' % (', '.join(metadatas) + ', IP, PID', '", "'.join([re.sub(cls.__re, '', obj[metadata].replace('"', "'")) for metadata in metadatas]), HOSTIP, PID)
        except Exception as e:
            LOG.error('数据插入mysql出错,组装SQL语句, 错误信息:%s', str(e))
            return
        try:
            # if not cls.__con.ping():
            #    cls.__con.close()
            #    cls.getConn(CF)
            con = cls.getConn()
            cur = con.cursor()
            cur.execute(save_sql)
            cur.close()
            #cls.__con.insert_id()
            #obj.setId(cls.__con.insert_id())
            if autocommit :
                con.commit()
            con.close()
        except Exception as e:
            LOG.error('数据插入mysql出错,SQL语句:%s, 错误信息:%s', save_sql, str(e))

    @classmethod
    @__openclose
    def savelog(cls, url, msg, str_order, errcode):
        try:
            log_sql = 'insert into t_log (url,msg,str_order,errcode,ip,pid) values ("%s","%s","%s","%s", "%s", "%s")' %(url,msg,str_order,errcode,HOSTIP,PID)
        except Exception as e:
            LOG.error('错误日志插入mysql出错,组装SQL语句, 错误信息:%s', str(e))
            return
        try:
            # if not cls.__con.ping():
            #    cls.__con.close()
            #    cls.getConn(CF)
            con = cls.getConn()
            cur = con.cursor()
            cur.execute(log_sql)
            cur.close()
            con.commit()
            con.close()
        except Exception as e:
            LOG.error('错误日志插入mysql出错,执行SQL语句:%s, 错误信息:%s', log_sql, str(e))

    @classmethod
    def deposit(cls):
        try:
            if cls.__pool is not None:
                cls.__pool.close()
                cls.__pool = None
                LOG.info('关闭数据库连接池成功!')
        except Exception as e:
            LOG.error('关闭数据库连接池出错!错误信息:%s', str(e))

if __name__ == '__main__':
    #print(type(MySqlEx.save))
    MySqlEx.savelog('text', 'text', '123', 'success')
    MySqlEx.savelog('text', 'text', '1234', 'success')
    MySqlEx.savelog('text', 'text', '1235', 'success')
    MySqlEx.savelog('text', 'text', '1236', 'success')
    MySqlEx.deposit()