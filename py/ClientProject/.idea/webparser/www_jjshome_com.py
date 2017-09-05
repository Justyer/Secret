# -*- coding: utf-8 -*-
#单例测试导入路径
if __name__ == '__main__':
    import sys, os
    parent_path = os.path.dirname(os.getcwd())
    sys.path.append(parent_path)

from webparser.webparserbase import ParserBase
from serializ.htmlfile import *
from serializ.oracle import *
from bean.urlbean import *
from log.logger import *
import datetime

LOG=logging.getLogger()
LOG.handlers[0].setLevel(logging.INFO)
LOG.handlers[1].setLevel(logging.INFO)

################################
metadatas = ('RECMETAID',
         '题名',
         '来源链接',
         '小区名称',
         '所属区域',
         '小区链接',
         '楼栋名称',
         '地址',
         '建成年份',
         '总层数',
         '当前层',
         '朝向',
         '建筑面积',
         '使用面积',
         '产权性质',
         '装修情况',
         '户型',
         '卧室数量',
         '客厅数量',
         '卫生间数量',
         '厨房数量',
         '阳台数量',
         '单价',
         '总价',
         '挂牌时间',
         '房屋图片',
         '信息来源',
         '联系人',
         '所属公司',
         '联系电话',
         '纬度',
         '经度',
         '备注',
         '预留字段',
         '房源编号',
         '发布时间',
         '住宅类别',
         '建筑类别',
         '配套设施',
         '估价链接',
         '租金链接',
         '房屋标签',
         '交通状况',
         '街景地图场景ID',
         '地图链接',
         '楼盘详情和所属HTML',
         '楼盘物业类型',
         '楼盘绿化率',
         '楼盘物业费',
         '楼盘物业公司',
         '楼盘开发商',
         '本月均价',
         '楼盘价格走势',
         '小区详情走势图链接',
         '经纪人链接',
         '经纪人图片链接',
         '小区成交历史链接',
         '城市',
         '行政区',
         '数据来源',
         'STR_ORDER')                                                                          #65

def format_str(s):
    return s.replace("\r\n",'').replace("\n",'').replace(' ', '').replace("\t",'').replace("\r",'').replace('\xa0','').lstrip().replace('&nbsp;','')

import requests, re
from bs4 import BeautifulSoup, Tag

def login(username='13836126857', password='sa123456', session=None):
    if session is not None:
        session.close()
    s = requests.session()
    s.headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36 LBBROWSER', 'Connection': 'keep-alive'}
    r = s.get("http://shenzhen.jjshome.com/hq/index")
    r = s.post("http://shenzhen.jjshome.com/login/loginUser", data={"loginName":username, "password":password})
    data = r.json()
    if data["success"]!=True:
        LOG.error("登录失败,返回数据!", data)
    LOG.info("登录成功!")
    return s

#解析中原地产真是成交数据
class wwwjjshomecom(ParserBase):
    headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36 LBBROWSER', 'Connection': 'keep-alive'}
    htmlwrite = HtmlFile()

    def __init__(self):
        super(wwwjjshomecom, self).__init__()
        self._s = None

    #默认定义间隔30分钟重新登录
    def getSession(self):
        nt = datetime.datetime.now()
        if self._s is None or (hasattr(self, '_lastLoginDT') and (nt - self._lastLoginDT).seconds>=30*60):
            self._lastLoginDT = nt
            self._s = login(session = self._s)
        return self._s

    #加载城市页面列表
    def default(self, urlbase):
        LOG.info('家家顺交易采集范围')
        citys = (("http://dongguan.jjshome.com/hq/index/s1n", 100), #北京 100页
                 ("http://foshan.jjshome.com/hq/index/s1n", 100),
                 ("http://guangzhou.jjshome.com/hq/index/s1n", 100),
                 ("http://huizhou.jjshome.com/hq/index/s1n", 100),
                 ("http://jiangmen.jjshome.com/hq/index/s1n", 100),
                 ("http://shenzhen.jjshome.com/hq/index/s1n", 100),
                 ("http://zhongshan.jjshome.com/hq/index/s1n", 100),
                 ("http://zhuhai.jjshome.com/hq/index/s1n", 100))
        i_order = urlbase.order+'0'
        ls = []
        for city in citys:
            for i in range(city[1]):
                ls.append(UrlBean("%s%d/" % (city[0], i+1), self.message('getpages'), order=i_order))
        return ls

    #解析城市二手房列表页
    def getpages(self, urlbase):
        LOG.info('jjshome getpages获得城市%s成交列表信息', urlbase.url)
        r = self.getSession().get(urlbase.url, headers=self.headers, timeout=(3.05, 2.5))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwjjshomecom %s 返回状态:%s', urlbase.url, r.status_code)
            return None
        html = r.text
        soup = BeautifulSoup(html, 'html.parser') #lxml
        i_order = urlbase.order+'1'
        ls = []
        d = {}  #定义结果集合
        fangall = soup.find_all('div', attrs={'class':'one-list clearfix'})
        for fang in fangall:
            jiage_all = fang.find_all('div',attrs={'class':'cj-data clearfix'})
            jiage_span = fang.find_all('span',attrs={'class':'fl w120'})
            if len(jiage_span) == 3:
                d['挂牌时间'] = jiage_span[0].find_all('span')[1].text
                d['总价'] = jiage_span[1].find_all('span')[1].text.replace('万', '')
                d['单价'] = jiage_span[2].find_all('span')[1].text.replace('元/m', '')
            d['城市'] = soup.find('span',attrs={'class':'change-city ml10'}).text.split('[')[0]
            fang_table = fang.find('div',attrs={'class':'list-cont'})
            fang_p = fang.find_all('p',attrs={'class':'pt0'})
            for fang_p_all in fang_p:
                fang_url_a = fang_p_all.find('a', attrs={'class':'tit'})
                d['题名'] = fang_url_a.text
                d['所属区域'] = d['题名'].split(' ')[1]
                d['户型'] = d['题名'].split(' ')[3]
                d['卧室数量'] = d['题名'].split(' ')[3].replace('居室', '')
                d['建筑面积'] = d['题名'].split(' ')[4].replace('平米', '')
                if fang_url_a['href']:
                    laiyuanlianjie = "%s%s" % ('/'.join(r.url.split('/')[:3]), fang_url_a['href'])
                    d['来源链接'] = laiyuanlianjie
                    ls.append(UrlBean(laiyuanlianjie, self.message('getitem'), key=laiyuanlianjie, param=dict(d), order=i_order))
        return ls

    #解析详细页面信息
    def getitem(self, urlbase):
        LOG.info('jjshome getitem获得城市%s挂牌详细信息', urlbase.url)
        t1 = time.time()
        r = self.getSession().get(urlbase.url, headers=self.headers, timeout=(3.05, 2.5))
        t2 = time.time()
        LOG.info('处理centanetgetpages请求getitem耗时:%f' % (t2-t1))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        #存储页面信息
        t1 = time.time()
        self.htmlwrite.save('%s\\%s\\%s' %(self.__class__.__name__, '真实成交', r.url.split('.')[0].split('/')[-1]), r.url, r.text)
        t2 = time.time()
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwcentanetcom %s 返回状态:%s', r.request.url, r.status_code)
            return
        t1 = time.time()
        html_x = r.text
        soup_x = BeautifulSoup(html_x, 'html.parser') #lxml
        d = urlbase.param

        neirong = soup_x.find('div',attrs={'class':'list clearfix'})
        p_1 = neirong.find('p',attrs={'class':'clearfix f16 pt15 c333'})
        p_span_all = p_1.find_all('span')
        if len(p_span_all) == 3:
            d['总层数'] = re.search(r'([^层/]*)[层/]*共?(\d*)层', p_span_all[0].text).group(2)
            d['当前层'] = re.search(r'([^层/]*)[层/]*共?(\d*)层', p_span_all[0].text).group(1)
            d['朝向'] = p_span_all[1].text
            d['装修情况'] = p_span_all[2].text
            p_2 = neirong.find('p',attrs={'class':'f16 c333 pt10'}).text.split('/')[0]
            d['小区名称'] = p_2.split(' ')[1]
            try:
                d['建成年份'] = neirong.find('p',attrs={'class':'f16 c333 pt10'}).text.split('/')[1].replace('年建', '')
            except:
                d['建成年份'] = ''
            d['经度'] = re.findall('<p class="f12 c666 pt10"><a href="javascript:;" class="links checkMap" comLng = "(.*?)" comLan =',html_x,re.S)[0]
            d['纬度'] = re.findall('" comLan = "(.*?)"',html_x,re.S)[0]
            d['小区链接'] = ''
            d['地址'] = ''
            d['RECMETAID']= ''
            d['楼栋名称']=''
            d['使用面积']=''
            d['产权性质']=''
            #d['装修情况']=''
            #d['卧室数量']=''
            d['客厅数量']=''
            d['卫生间数量']=''
            d['厨房数量']=''
            d['阳台数量']=''
            d['建筑类别'] = ''
            d['房屋图片']=''
            d['信息来源']=''
            d['联系人']=soup_x.find('div', class_='jjr-box').find('span', class_='mt10').text
            d['所属公司']=''
            d['联系电话']=soup_x.find('div', class_='jjr-box').find('span', class_='tel').text
            d['备注']=''
            d['预留字段']=''
            d['房源编号']=''
            d['发布时间']=''
            d['住宅类别']=''
            d['配套设施']=''
            d['估价链接']=''
            d['租金链接']=''
            d['房屋标签']=''
            d['交通状况']=''
            d['街景地图场景ID']=''
            d['地图链接']=''
            d['楼盘详情和所属HTML']=''
            d['楼盘物业类型']=''
            d['楼盘绿化率']=''
            d['楼盘物业费']=''
            d['楼盘物业公司']=''
            d['楼盘开发商']=''
            d['本月均价']=''
            d['楼盘价格走势']=''
            d['小区详情走势图链接']=''
            d['经纪人链接']=''
            d['经纪人图片链接']=''
            d['小区成交历史链接']=''
            d['行政区']=d['所属区域']
            # x = format_str(d['RECMETAID'])+'\t'+format_str(d['题名'])+'\t'+format_str(d['来源链接'])+'\t'+format_str(d['小区名称'])+'\t'+d['所属区域'] +'\t'+ format_str(d['小区链接'])+'\t'+format_str(d['楼栋名称'])+'\t'+format_str(d['地址'])+'\t'+format_str(d['建成年份'])+'\t'+format_str(d['总层数'])+'\t'+format_str(d['当前层'])+'\t'+format_str(d['朝向'])+'\t'+format_str(d['建筑面积'])
            # y = format_str(d['使用面积'])+'\t'+format_str(d['产权性质'])+'\t'+format_str(d['装修情况'])+'\t'+format_str(d['户型'])+'\t'+format_str(d['卧室数量'])+'\t'+format_str(d['客厅数量'])+'\t'+format_str(d['卫生间数量'])+'\t'+format_str(d['厨房数量'])+'\t'+format_str(d['阳台数量'])+'\t'+format_str(d['单价'])+'\t'+format_str(d['总价'])
            # z = format_str(d['挂牌时间'])+'\t'+format_str(d['房屋图片'])+'\t'+format_str(d['信息来源'])+'\t'+format_str(d['联系人'])+'\t'+format_str(d['所属公司'])+'\t'+format_str(d['联系电话'])+'\t'+format_str(d['纬度'])+'\t'+format_str(d['经度'])+'\t'+format_str(d['备注'])+'\t'+format_str(d['预留字段'])+'\t'+format_str(d['房源编号'])
            # w = format_str(d['发布时间'])+'\t'+format_str(d['住宅类别'])+'\t'+format_str(d['建筑类别'])+'\t'+format_str(d['配套设施'])+'\t'+format_str(d['估价链接'])+'\t'+format_str(d['租金链接'])+'\t'+format_str(d['房屋标签'])+'\t'+format_str(d['交通状况'])+'\t'+format_str(d['街景地图场景ID'])+'\t'+format_str(d['地图链接'])+'\t'+format_str(d['楼盘详情和所属HTML'])
            # q = format_str(d['楼盘物业类型'])+'\t'+format_str(d['楼盘绿化率'])+'\t'+format_str(d['楼盘物业费'])+'\t'+format_str(d['楼盘物业公司'])+'\t'+format_str(d['楼盘开发商'])+'\t'+format_str(d['本月均价'])+'\t'+format_str(d['楼盘价格走势'])+'\t'+format_str(d['小区详情走势图链接'])+'\t'+format_str(d['经纪人链接'])+'\t'+format_str(d['经纪人图片链接'])+'\t'+format_str(d['小区成交历史链接'])+'\t'+format_str(d['城市'])+'\t'+format_str(d['行政区'])
            # print(x+'\t'+y+'\t'+z+'\t'+w+'\t'+q)
            # with open('jj_zhuhai.txt', 'a+', encoding='utf8') as f:
            #     f.write(x + '\t' + y + '\t' + z + '\t' + w + '\t' + q + '\n')
            #     f.flush()
            for meta in d:
                d[meta] = format_str(d[meta])
            # print(x+'\t'+y+'\t'+z+'\t'+w+'\t'+q)
            # with open('zy_1101_2016-02-14.txt', 'a+', encoding='utf8') as f:
            #     f.write(x+'\t'+y+'\t'+z+'\t'+w+'\t'+q+'\n')
            #     f.flush()
            d['数据来源'] = 'jjs'
            d['STR_ORDER']=urlbase.order
            self.completionlr(d, metadatas)
            MySqlEx.savecj(d, metadatas)
        t2 = time.time()
        LOG.info('解析页面耗时:%f' % (t2-t1))

if __name__ == '__main__':
    wwwjjshomecom = wwwjjshomecom()
    for page in wwwjjshomecom.default(UrlBase('http://www.jjshome.com', 'wwwjjshomecom',order='1603070948')):
        for item in wwwjjshomecom.getpages(page):
            wwwjjshomecom.getitem(item)
    #wwwjjshomecom.getitem(item)

    #item = wwwjjshomecom.getpages(UrlBean('http://bj.centanet.com/chengjiao/g1', 'wwwjjshomecom#getpages', order='16030709480'))[0]
    #wwwcentanetcom.getitem(UrlBean('http://bj.centanet.com/chengjiao/160221101701ab7e4d03b0e7088b39fa.html', 'wwwcentanetcom#getitem', order='160307094801'))