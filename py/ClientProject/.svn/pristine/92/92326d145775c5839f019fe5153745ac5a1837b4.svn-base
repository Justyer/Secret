import re
from util.UtilityGcs import GcsConverUtil
#定义解析器父类
class ParserBase(object):
    SPLIT = '#'     #消息格式    类名#方法名
    def __init__(self):
        #print(self.__class__)
        pass
    def message(self, method):
        #print('%s%s%s' % (self.__class__.__name__, self.SPLIT, method))
        return ('%s%s%s'% (self.__class__.__name__, self.SPLIT, method))
    #登录方法
    def login(self):
        pass
    #发送请求前
    def before(self):
        pass
    #发送请求后
    def after(self):
        pass
    #解析网站返回URL列表
    def getlist(self):
        pass
    #解析网站内容返回具体信息
    def getpage(self):
        pass
    #补全输出值
    def completionlr(self,lr,metadatas):
        for item in metadatas:
            try:
                lr[item]
            except:
                lr[item] = ''
        return lr
    #获得小区坐标
    def getbaidugcs(self,xqname,city):
        try:
            js = GcsConverUtil.getbaidugcs(xqname, city)
            return '%s,%s'%(js['result']['location']['lng'], js['result']['location']['lat'])
        except Exception as e:
            return ''
    #处理文件名称
    def duefname(self, fname, repl=''):
        return re.sub(r'[\\/:*?"<>|]*', repl, fname)