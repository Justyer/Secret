#单例测试导入路径
if __name__ == '__main__':
    import sys, os
    parent_path = os.path.dirname(os.getcwd())
    sys.path.append(parent_path)

import pymysql, re, socket
from pymysql.cursors import DictCursor
from DBUtils.PooledDB import PooledDB

from log.logger import *
LOG=logging.getLogger()
LOG.handlers[0].setLevel(logging.INFO)
LOG.handlers[1].setLevel(logging.DEBUG)


global HOSTIP,PID
HOSTIP = str(socket.gethostbyname(socket.gethostname()))
PID = str(os.getpid())

#数据库工具类
class MySqlEx():
    __pool = None
    __re = re.compile(r'\s')

    @staticmethod
    def __getConn():
        if MySqlEx.__pool is None:
            __pool = PooledDB(host='localhost', port=3306, db='gxd',
                              user='root', passwd='123456',
                              creator=pymysql,
                              mincached=6,
                              maxcached=6,
                              maxconnections=6,
                              blocking=False,
                              use_unicode=True,
                              charset='utf8',
                              cursorclass=DictCursor)
        return __pool.connection()

    def __openclose(f):
        def fn(*args, **kw):
            try:
                __con = MySqlEx.__getConn()
                LOG.info('连接%s主机%s数据库成功!')
                __cur = __con.cursor()
                LOG.info('打开cursor成功!')
            except Exception as e:
                LOG.error('连接mysql出错,错误信息:%s', str(e))
            kw['con'] = __con
            kw['cur'] = __cur
            fr = f(*args, **kw)
            # try:
            #     if __cur is not None:
            #         __cur.close()
            #         __cur = None
            #         LOG.info('关闭cursor')
            # except Exception as e:
            #     LOG.error('关闭连接出错!错误信息:%s', str(e))
            # finally:
            #     if __con is not None:
            #         __con.close()
            #         __con = None
            #         LOG.info('关闭connect')
            return fr
        return fn

    @staticmethod
    @__openclose
    def save(obj, metadatas, autocommit=True, con=None, cur=None):
        try:
            #将信息转换成SQL语句
            sql = 'insert into t_esf (%s) values ("%s","%s","%s")' % (', '.join(metadatas) + ', IP, PID', '", "'.join([re.sub(MySqlEx.__re, '', obj[metadata].replace('"', "'")) for metadata in metadatas]), HOSTIP, PID)
            #if not self.__con.ping():
            #    self.close()
            #    self.init()
            cur.execute(sql)
            #self.__con.insert_id()
            #obj.setId(self.__con.insert_id())
            if autocommit :
                con.commit()
        except Exception as e:
            LOG.error('数据插入mysql出错,SQL语句:%s, 错误信息:%s', sql, str(e))

    @staticmethod
    @__openclose
    def savelog(url, msg, errcode, con=None, cur=None):
        try:
            sql = 'insert into t_log (url,msg,errcode,HOSTIP,PID) values ("%s","%s","%s","%s", "%s")' %(url,msg,errcode,HOSTIP,PID)
            #if not self.__con.ping():
            #    self.close()
            #    self.init()
            cur.execute(sql)
            con.commit()
        except Exception as e:
            LOG.error('错误日志插入mysql出错,SQL语句:%s, 错误信息:%s', sql, str(e))

if __name__ == '__main__':
    print(type(MySqlEx.save))
    MySqlEx.savelog('text', 'text', 'success')