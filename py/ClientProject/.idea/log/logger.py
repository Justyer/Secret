import logging
from logging.handlers import TimedRotatingFileHandler

import sys, os
parent_path = os.path.dirname(os.getcwd())
sys.path.append(parent_path)
#自定义引用
from log.message import *

logpath=os.path.split(os.path.realpath(__file__))[0].split(':')[0] + ':\\gxd\\log'
if not os.path.exists(logpath):
    os.makedirs(logpath)

#初始化日志系统
logging.basicConfig(level=logging.INFO, datefmt=None,
                    format='%(asctime)-24s level-%(levelname)-12s thread-%(thread)-6d %(module)-s.%(funcName)-10s Line:%(lineno)-4d %(message)s',
                    handlers=[logging.StreamHandler(), TimedRotatingFileHandler(logpath+'\\'+str(os.getpid())+'_client.log', when='D', interval=1, backupCount=15)])
global LOG
LOG=logging.getLogger()
LOG.handlers[0].setLevel(logging.DEBUG)
LOG.handlers[1].setLevel(logging.INFO)
"""
LOG.debug('调试信息')
LOG.info('有用的信息')
LOG.warning('警告信息')
LOG.error('错误信息')
LOG.critical('严重错误信息')"""