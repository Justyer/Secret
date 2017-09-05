import multiprocessing, time, math, re, threading, pickle
import xmlrpc.client

from bean.urlbean import *
from dispatch.urldispatch import UrlDispatch
from webparser.www_58_com import *
from webparser.www_fang_com import *
from webparser.www_ajk_com import *
from webparser.www_gj_com import *
from webparser.www_fang_com_smallcity import *
from webparser.www_worldunion_com import *
from webparser.www_xt_com import *
from webparser.www_xt_com_other import *
from webparser.www_lj_com import *
from webparser.www_centanet_com import *
from webparser.www_lianjia_cj_com import *
from webparser.www_sfcj_com import *
from webparser.www_jjshome_com import *
from webparser.www_bx_com import *
from webparser.www_cszg_com import *
from webparser.www_fangdi_com import *
from webparser.www_zzfdc_com_cn import *
from log.logger import *
import config

#s = xmlrpc.client.ServerProxy('http://localhost:80')
#print(s.system.listMethods())
global WORKERS, JOBFETCH, TRYINTERVAL, FETCHTERVAL
WORKERS = 2        #任务线程数
JOBFETCH = 20      #每次获取任务个数
TRYINTERVAL = 1*10 #客户端重连间隔10秒重连
FETCHTERVAL = 1*5  #客户端重新获取数据间隔5秒
JOBBACK = 100      #单次返回200个任务
#socket.setdefaulttimeout(15)

global BADFILE
BADFILE = "\\".join(os.path.split(os.path.realpath(__file__))[0].split("\\")[:-2]) + "\\jobs.bad"

class Worker(threading.Thread):

    def __init__(self, num, interval):
        threading.Thread.__init__(self)
        self.num = num
        self.interval = interval
        self.stop = False
        self.tryinterval = TRYINTERVAL
        self.fetchterval = FETCHTERVAL
        self.JOBBACK = JOBBACK
        self.failedJob = []         #失败任务列表, 需要持久化
        self.failedNextJob = []     #失败返回值列表, 需要持久化
        self.sp = None

    def run(self):
        #消息分发，根据URL和消息定位需要解析的方法
        self.urldispatch = UrlDispatch([www58com,wwwfangcom,wwwajkcom,wwwgjcom,wwwfangcomSC,
                                        wwwworldunioncom,wwwworldunioncomex,
                                        wwwxtcom,wwwxtcomother,wwwljcom,
                                        wwwcentanetcom,wwwlianjiacjcom,wwwsfcjcom,wwwjjshomecom,
                                        wwwbxcom,wwwcszgcom,
                                        wwwfangdicom,wwwzzfdccomcn])
        #始终进行重新连接
        while (not self.stop):
            #定义所有的主机地址
            serveriplist = []
            hasmaster = False
            #读取配置文件,获得服务器地址
            try:
                serveriplist.append(config.CF.get('server', 'master'))
                hasmaster = True
            except Exception as e:
                LOG.warning('读取服务器IP端口配置出错,异常信息%s,异常类型%s!', str(e), type(e))
            try:
                serveriplist.append(config.CF.get('server', 'slave'))
                LOG.info("读取配置文件, servers_ip_port:%s", ':master, slave:'.join(serveriplist))
            except Exception as e:
                LOG.warning('读取服务器IP端口配置出错,异常信息%s,异常类型%s!', str(e), type(e))
                LOG.warning('%d秒后重新读取服务器IP端口配置!', self.tryinterval)
                if not hasmaster:
                    time.sleep(self.tryinterval)
                    continue

            #连接RPC服务
            connected = False
            for servip in serveriplist:
                if isinstance(self.sp, xmlrpc.client.ServerProxy):
                    self.sp("close")()
                    del self.sp
                self.sp = xmlrpc.client.ServerProxy('http://%s' % (servip), allow_none=True)
                self.sp("transport").__class__.encode_threshold=512      #设置Gzip的压缩门槛

                try:
                    #获取配置信息
                    config.merageDB(self.sp.getcf())
                except Exception as e:
                    LOG.error('读取%s服务器配置文件出错, 异常信息%s, 异常类型%s!', servip, str(e), type(e))
                    time.sleep(1)
                    continue
                connected = True
                LOG.info("连接服务器:%s", servip)
                break
            #连接未成功
            if (not connected):
                LOG.error(ERROR.CLIENT_CONNECT_FAILE, self.tryinterval)
                time.sleep(self.tryinterval)
                continue
            #连接成功开始获取数据，等待线程被停止
            while (not self.stop):
                #尝试将错误列表里的内容再次写库
                try:
                    l = []
                    if self.failedJob:
                        l = self.failedJob[:]
                        self.failedJob.clear()
                    if self.failedNextJob:
                        l.extend(self.failedNextJob)
                        self.failedNextJob.clear()
                    if l:
                        #分批次添加任务
                        lf = l
                        try:
                            for bath in range(0, math.ceil(len(l)/self.JOBBACK)):
                                self.sp.addJobs(l[bath*self.JOBBACK:(bath+1)*self.JOBBACK]) #添加任务有可能出错，需要进一步细化修改
                                del lf
                                lf = l[(bath+1)*self.JOBBACK:]
                                if bath>=1:
                                    time.sleep(0.5)
                        except Exception as e:
                            LOG.error("分批返回错误任务失败!%s%s", str(e), type(e))
                            self.failedNextJob.extend(lf)
                except ConnectionRefusedError as e:
                    LOG.error('失败任务返回服务器,服务器通讯中断,尝试%d秒后重新连接服务器,异常信息%s,异常类型%s!', self.tryinterval, str(e), type(e))
                    time.sleep(self.tryinterval)
                    break
                except Exception as e:
                    LOG.error('失败任务返回服务器出错,异常信息%s,异常类型%s!', str(e), type(e))
                try:
                    t1 = time.time()
                    jobs = self.sp.getJobs(JOBFETCH)
                    t2 = time.time()
                    LOG.info('从服务器获取数据耗时:%.3f秒', (t2-t1))
                    if jobs is None or len(jobs)==0:
                        LOG.info('未从服务器待发队列取得任务, %d秒之后再尝试获取!', self.fetchterval)
                        time.sleep(self.fetchterval)
                        continue
                #跳出重新连接RPC服务
                except ConnectionRefusedError as e:
                    LOG.error('从服务器获取数据任务失败,服务器通讯中断,尝试%d秒后重新连接服务器, 异常信息%s,异常类型%s!', self.tryinterval, str(e), type(e))
                    time.sleep(self.tryinterval)
                    break
                except Exception as e:
                    LOG.error('从服务器获取数据任务失败,异常信息%s,异常类型%s!', str(e), type(e))
                    continue
                #线程获取任务数量
                LOG.info(DEBUG.WORK_GETJOB, self.num, len(jobs))
                #对URL进行分发
                for i in jobs:
                    #存在类变量就直接实例化类
                    urlbean = None
                    nextjobs = None
                    try:
                        #获得class并且删除该属性
                        classname = i['_UrlBase__classname']
                        i.pop('_UrlBase__classname')
                        urlbean = globals()[classname](**i)
                    except Exception as e:
                        #处理失败就处理下一个任务,任务被丢弃,记录数据库留作审计
                        LOG.error(ERROR.CLIENT_NEWFAILE, str(e), type(e))
                        try:
                            MySqlEx.savelog(i.url, i.message, i.order, ERROR.CLIENT_NEWFAILE % (str(e), type(e)))
                        except Exception as e:
                            LOG.error("写错误日志时发生错误,错误信息:%s!", str(e))
                        continue
                    #如果处理失败，将此任务返回服务器队列
                    rs = False
                    nextjobs = []
                    try:
                        rs, nextjobs = self.urldispatch.dispatch(urlbean)
                    except Exception as e:
                        LOG.error(ERROR.CLIENT_RETURNURLS_FAILE, str(rs), str(e), type(e))
                        try:
                            MySqlEx.savelog(urlbean.url, urlbean.message, urlbean.order, ERROR.CLIENT_RETURNURLS_FAILE % (str(rs), str(e), type(e)))
                        except Exception as e:
                            LOG.error("写错误日志时发生错误,错误信息:%s!", str(e))
                    #未成功任务返回服务器重新分发
                    if not rs:
                        try:
                            #记录错误次数
                            urlbean.trytimes += 1
                            #任务返回服务器
                            self.failedJob.append(urlbean)        #添加任务有可能出错，需要进一步细化修改
                            LOG.warning(WARN.CLIENT_MESSAGE_FAILED, urlbean.url)
                        except Exception as e:
                            LOG.error('返回错误任务时出现异常, 异常信息%s, 异常类型%s, url:%s', str(e), type(e), urlbean.url)  #任务未处理完
                            #time.sleep(self.fetchterval)
                    else:
                        try:
                            t1 = time.time()
                            if nextjobs:
                                left = nextjobs
                                #大量任务时按预定义的单批上限个数分批返回
                                for bath in range(0, math.ceil(len(nextjobs)/self.JOBBACK)):
                                    self.sp.addJobs(nextjobs[bath*self.JOBBACK:(bath+1)*self.JOBBACK]) #添加任务有可能出错，需要进一步细化修改
                                    del left
                                    left = nextjobs[(bath+1)*self.JOBBACK:]
                                    if bath>=1:
                                        time.sleep(0.5)
                            t2 = time.time()
                            LOG.info('向服务器传递数据耗时:%.3f' % (t2-t1))
                        except Exception as e:
                            if left is not None:
                                self.failedNextJob.extend(left)
                            LOG.error('返回新任务时与服务器连接断开, 异常信息%s, 异常类型%s', str(e), type(e))  #任务未处理完
                #暂停一段时间处理下一个任务
                time.sleep(self.interval)
        #客户端线程将要退出
        LOG.info(INFO.CLIENT_CLOSED)
        #关闭链接
        try:
            self.sp("close")()
            MySqlEx.deposit()
        except Exception as e:
            LOG.error('关闭程序出错, 异常信息%s, 异常类型%s', str(e), type(e))

#从磁盘加载数据
def loadfromdisk():
    baddata = None
    #加载失败任务到第一个线程内存
    try:
        with open(BADFILE,'rb') as f:
            baddata = pickle.load(f)
        LOG.info("读取失败任务成功,保存位置:%s", BADFILE)
    except Exception as e:
        LOG.warning("读取失败任务时发生错误,保存位置:%s,异常信息%s,异常类型%s", BADFILE, str(e), type(e))
    return baddata

def savetodisk(workers):
    #保存失败的任务到文件
    failedJob = []
    failedNextJob = []
    for w in workers:
        if (len(w.failedJob)>0 or len(w.failedNextJob)>0):
            failedJob.extend(w.failedJob)
            failedNextJob.extend(w.failedNextJob)
    try:
        with open(BADFILE,'wb') as f:
            pickle.dump(dict(failedJob=failedJob, failedNextJob=failedNextJob),f)
        LOG.info("保存失败任务成功,保存位置:%s", BADFILE)
    except Exception as e:
        LOG.error("保存失败任务时发生错误,保存位置:%s,异常信息%s,异常类型%s", BADFILE, str(e), type(e))

#链接服务器获取页面
if __name__ == '__main__':
    workerinterval = 0.5
    workers = []
    mainworker = Worker(0, workerinterval)
    if '-ig' not in sys.argv:
        baddata = loadfromdisk()
        if baddata is not None:
            mainworker.failedJob = baddata['failedJob']
            mainworker.failedNextJob = baddata['failedNextJob']
    mainworker.start()
    workers.append(mainworker)
    for i in range(1, WORKERS):
        worker = Worker(i, workerinterval)
        worker.start()
        workers.append(worker)
    for w in workers:
        w.join()
    if '-ig' not in sys.argv:
        savetodisk(workers)
    LOG.info("10秒后重启程序!")
    time.sleep(10)
    #重启程序
    #os.execl(sys.executable, sys.executable, *sys.argv)






"""
import zerorpc
c=zerorpc.Client()
c.connect("tcp://127.0.0.1:4242")#连接RPC服务端
print (c.hello('www.ruifengyun.com'))
"""
"""
import zmq
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://127.0.0.1:5000")
socket.connect("tcp://127.0.0.1:6000")

for i in range(10):
    msg = "msg %s" % i
    socket.send_string(msg)
    print ("Sending", msg)
    msg_in = socket.recv()
"""

