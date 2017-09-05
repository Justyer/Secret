#单例测试导入路径
if __name__ == '__main__':
    import sys, os
    parent_path = os.path.dirname(os.getcwd())
    sys.path.append(parent_path)

import time
from log.logger import LOG
from bean.urlbean import *
from webparser.webparserbase import ParserBase
from log.message import *
from serializ.oracle import *

from requests.exceptions import *
from dispatch.pydecorator import *

#处理重试异常信息
def errorhook(tries_remaining, exception, delay):
    LOG.error('自定义脚本处理URL任务异常, %d秒后重试, 还可以重试%d次, 异常信息:%s, 异常类型:%s', delay, tries_remaining, str(exception), type(exception))

#根据消息来分发URL处理包
class UrlDispatch(object):
    SPLIT = '#'     #消息格式    类名#方法名
    def __init__(self, parsers=None):
        self.__dispatch = {}
        if parsers and isinstance(parsers, list):
           for pa in parsers:
               if pa and isinstance(pa, type) and issubclass(pa, ParserBase):
                   self.__dispatch[pa.__name__]=pa()  #由分发器来实例化,有登陆的网站时要考虑SESSION过期的问题
                   LOG.info(INFO.URLDISPATCH_REG % (pa.__name__))
               else:
                   LOG.warn(WARN.URLDISPATCH_PARSERS_SUB_ERR, type(pa))
        else:
            LOG.warn(WARN.URLDISPATCH_PARSERS_TYPE_ERR + type(parsers))
        LOG.info(INFO.URLDISPATCH_START)

    @retries(3, delay=1, backoff=1, exceptions=(ReadTimeout, ConnectTimeout, Timeout, URLRequired, TooManyRedirects, SSLError, ProxyError, ConnectionError, HTTPError, RequestException), hook=errorhook)
    def callparserfun(self, p, funname, urlbase):
        nextjobs = []
        nextjobs = getattr(p, funname)(urlbase)
        return nextjobs

    def dispatch(self, urlbase):
        nextjobs = []
        try:
            if urlbase is None or not isinstance(urlbase, UrlBase):
                LOG.warn(WARN.URLDISPATCH_MESSAGE_FORMATERR)
                return False, None
            msg = urlbase.getmessage()
            msgpartl = None
            if not msg or not isinstance(msg, str):
                LOG.warn(WARN.URLDISPATCH_MESSAGE_FORMATERR)
                return False, None
            msgpartl = msg.split(self.SPLIT)
            if len(msgpartl)<1:
                LOG.warn(WARN.URLDISPATCH_MESSAGE_FORMATERR)
                return False, None
            p = self.__dispatch.get(msgpartl[0], None)
            if not p:
                LOG.warn(WARN.URLDISPATCH_MESSAGE_PARSERERR, msgpartl[0])
                return False, None
            funname = 'default' if len(msgpartl)==1 else  msgpartl[1]
            if hasattr(p, funname):
                try:
                    nextjobs = self.callparserfun(p, funname, urlbase)
                except Exception as e:
                    LOG.error("执行脚本出错, url%s, 消息内容%s, 错误信息%s", urlbase.url, urlbase.getmessage(), str(e))
                    try:
                        MySqlEx.savelog(urlbase.url, urlbase.getmessage(), urlbase.order, str(e))
                    except Exception as e:
                        LOG.error("写错误日志时发生错误,错误信息:%s!", str(e))
                    return False, None
            else:
                LOG.warn("解析脚本%s, 没有指定的解析方法", p.__class__.__name__, funname)
            LOG.debug(DEBUG.URLDISPATCH_DISPATCH % (msgpartl[0], funname))
        except Exception as e:
            LOG.error(WARN.URLDISPATCH_ERROR, urlbase.url, str(e))
            try:
                MySqlEx.savelog(urlbase.url, urlbase.getmessage(), urlbase.order, str(e))
            except Exception as e:
                LOG.error("写错误日志时发生错误,错误信息:%s!", str(e))
            return False, None
        return True, nextjobs

"""
if __name__ == '__main__':
    #print(issubclass(www58com, ParserBase))
    #print(type(www58com)== type)
    try:
        UrlDispatch([www58com, 123]).dispatch(UrlBase('www.58.com', 'www58com#getcitys'))
    except Exception as e:
        print('ERR'+str(e))
"""