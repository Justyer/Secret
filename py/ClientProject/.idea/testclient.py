import sys, os, socket, time, xmlrpc.client, threading
from log.logger import *
from bean.urlbean import *

class Worker(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        localip = socket.gethostbyname(socket.gethostname())
        self.s = xmlrpc.client.ServerProxy('http://%s:6789' % (localip), allow_none=True)

    def run(self):
        while (True):
            try:
                ls = []
                ls = self.s.getJobs(20)
                for l in ls:
                    re = []
                    #根
                    if "getpage" in l["message"]:
                        #生成任务
                        for i in range(200):
                            re.append(UrlBean('http://bj.58.com/ershoufang/', 'www58com#getitem', key="www58com#getitem"+str(i), param=10, headers='北京', order='1602221013'))
                        print("getpage!")
                        time.sleep(1)
                    elif "getitem" in l["message"]:
                        print("getitem!")
                        time.sleep(1)
                    else:
                        #生成任务
                        for i in range(200):
                            re.append(UrlBean('http://bj.58.com/ershoufang/', 'www58com#getpage', param=10, headers='北京', order='1602221013'))
                        print("root")
                        time.sleep(2)
                    for i in range(3):
                        self.s.addJobs(re)
                        time.sleep(1)
                print("empty!")
                time.sleep(2)
            except Exception as e:
                print(str(e), type(e))

if __name__=='__main__':
    workers = []
    for i in range(1):
        worker = Worker()
        worker.start()
        workers.append(worker)
    for w in workers:
        w.join()