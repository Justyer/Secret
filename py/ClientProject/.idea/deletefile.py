import os, time, datetime, shutil
from log.logger import *

def delete():
    path = 'C:/gxd'
    fiveDayAgo = (datetime.datetime.now() - datetime.timedelta(days=5)).strftime('%Y-%m-%d')
    try:
        t1 = time.time()
        for root in os.walk(path+'/html'):
            if fiveDayAgo in root[0]:
                shutil.rmtree(root[0])
        t2 = time.time()
        LOG.info('deletefile删除%sHTML文件成功，耗时%.3f' % (str(fiveDayAgo),(t2-t1)))
    except Exception as e:
        LOG.error('deletefile删除HTML文件失败,%s' % str(e))
    try:
        t3 = time.time()
        for file in os.listdir(path+'/log'):
            if fiveDayAgo in file:
                os.remove(path+'/log/'+file)
        t4 = time.time()
        LOG.info('deletefile删除%sHTML日志成功，耗时%.3f' % (str(fiveDayAgo),(t4-t3)))
    except Exception as e:
        LOG.error('deletefile删除HTML日志失败,%s' % str(e))

while True:
    NowHour = datetime.datetime.now().strftime('%H')
    if NowHour in  ['04','05','06','07']:
        delete()
    time.sleep(14400)








