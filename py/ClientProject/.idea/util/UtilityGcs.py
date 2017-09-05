# coding:utf-8
import hashlib
from urllib.parse import quote, quote_plus
import requests


# 根据地址信息获取百度坐标
class GcsConverUtil:
    baiduhost = 'http://api.map.baidu.com'
    baiduapi = '/geocoder/v2/'
    # ak = 'UDKyoUAtLfCmXs2erIy9lvWG'
    # sk = 'jFY4BD5G756MLgOmRFpnfeg1YPghlfnN'
    ak = '3a345e5b8b56a7f80605cd95d64634a8'
    sk = ''

    @classmethod
    def getbaidugcs(cls, address, city=None):
        """
        :param address: 地址的中文名称
        :param city: 地址所在城市[可选项]
        :return:json结构结果集，其中lng即longitude，代表经度；lat即latitude，代表纬度
        结果集举例：{'status': 0, 'result': {'location': {'lat': 45.824041626811, 'lng': 126.56750659071}, 'level': '教育',
         'confidence': 40, 'precise': 0}}
        status为0时找到经纬度，返回含经纬度的字典，可用key为result下的key为location内找到；
        status为1时未找到
        """
        urlstr = '%s?address=%s&output=%s&ak=%s' % (
            cls.baiduapi, address, 'json', cls.ak) if not city else '%s?address=%s&city=%s&output=%s&ak=%s' % (
            cls.baiduapi, address, city, 'json', cls.ak)
        encodedurl = quote(urlstr, safe="/:=&?#+!$,;'@()*[]")
        rawStr = encodedurl + cls.sk
        sn = hashlib.md5(quote_plus(rawStr).encode()).hexdigest()
        r = requests.get('%s%s&sn=%s' % (cls.baiduhost, urlstr, sn))
        # print(address, r.json())
        return r.json()

    @classmethod
    def getcorrect(cls, lngx, lngy):
        r = requests.get('http://lbs.juhe.cn/api/baidu.php?lngx=%s&lngy=%s&type=2' % (lngx, lngy))
        return r.json()
