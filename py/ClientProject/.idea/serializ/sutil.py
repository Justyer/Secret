#定义序列化工厂解决对象不同序列化要求的问题
from math import ceil, fabs
class Sutil(object):
    #单条处理
    @classmethod
    def serializ(cls, s, stype):
        stype.init()
        try:
            stype.save(s)
        except Exception as e:
            print('序列化对象出现异常'+str(e))
        finally:
            stype.close()

    #批量处理
    @classmethod
    def serializl(cls, li, stype, rowcount=10000): #rowcount必须大于0
        if rowcount<=0:
            rowcount=10000
        stype.init()
        try:
            lcount = len(li)
            for i in range(0, lcount):
                stype.save(li[i], False)
                if(i+1)%rowcount!=0 and (i+1)!=lcount:
                    continue
                else:
                    stype.comm()
        except Exception as e:
            print('序列化数组对象出现异常'+str(e))
        finally:
            stype.close()
