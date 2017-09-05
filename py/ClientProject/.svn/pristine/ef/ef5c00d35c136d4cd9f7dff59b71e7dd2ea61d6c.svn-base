#加载配置信息
import configparser, os
from log.logger import LOG

def initcf():
    rootpath = '\\'.join(os.path.split(os.path.realpath(__file__))[0].split('\\')[:-2])
    clientinipath = rootpath + "\\client.ini"
    cf = configparser.ConfigParser()
    LOG.info(clientinipath)
    if cf.read(clientinipath):
        pass
    else:
        #初始化数据库
        #cf.add_section("db")
        #cf.set("db", "host", "localhost")
        #cf.set("db", "db", "gxd")
        #cf.set("db", "port", "3306")
        #cf.set("db", "user", "root")
        #cf.set("db", "passwd", "123456")
        #初始化服务器配置
        cf.add_section("server")
        #CRITICAL = 50 FATAL = CRITICAL ERROR = 40 WARNING = 30 WARN = WARNING
        #INFO = 20 DEBUG = 10 NOTSET = 0
        cf.set("server", "ip", "localhost")
        #cf.set("server", "loglevel", "10")
        cf.write(open(os.path.split(os.path.realpath(__file__))[0] + "\\client.ini","w"))
    return cf

def merageDB(section):
    global CF
    if not CF.has_section("db"):
        CF.add_section("db")
    for s in section:
        CF.set("db", s[0], s[1])

global CF
CF = initcf()

if __name__=='__main__':
    initcf()