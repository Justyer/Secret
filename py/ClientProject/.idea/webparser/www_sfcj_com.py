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
import datetime, time
from random import random

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
    return s.replace("\n",'').replace(' ', '').replace("\t",'').replace("\r",'').replace('\xa0','').lstrip().replace('&nbsp;','').replace("小区地址：",'').replace("查看地图",'').replace("地  址：",'').replace("小区网",'').replace("元/O",'')

import requests, re
from bs4 import BeautifulSoup, Tag
from requests.exceptions import RequestException
#解析中原地产真是成交数据
class wwwsfcjcom(ParserBase):
    headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36 LBBROWSER', 'Connection': 'keep-alive'}
    htmlwrite = HtmlFile()

    def __init__(self):
        super(wwwsfcjcom, self).__init__()

    #加载城市页面列表
    def default(self, urlbase):
        LOG.info('搜房成交数据采集')
        #url = 'http://fang.com/SoufunFamily.htm'
        page = requests.get(urlbase.url, headers=self.headers, timeout=(3.05, 3.5))
        soup = BeautifulSoup(page.text, 'html.parser')
        city = soup.find('table',attrs={'class':'table01','border':'0','cellspacing':'0','cellpadding':'0','id':'senfe'}).find_all('a')
        i_order = urlbase.order+'0'
        ls = []
        for city_a in city:
            if 'http' in city_a['href']:
                xl = city_a['href'].replace(' ', '')
                ls.append(UrlBean(city_a['href'], self.message('getqy'), param=city_a.text, order=i_order))
        return ls

    #解析城市区域信息
    #@retries(100, delay=1, backoff=1, exceptions=(RequestException))
    def getqy(self, urlbase):
        LOG.info('wwwsfcjcom %s 成交列表信息', urlbase.param)
        time.sleep(random()+2)
        r = requests.get(urlbase.url.strip(), headers=self.headers, timeout=(3.05, 3.5))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwlianjiacjcom %s 返回状态:%s', urlbase.url, r.status_code)
            return None
        html_city = r.content.decode('gbk', errors='ignore')
        soup_city = BeautifulSoup(html_city, 'html.parser') #lxml
        i_order = urlbase.order+'1'
        ls = []
        city_url = soup_city.find('div',attrs={'id':'dsy_D01_03'})
        if city_url is None:
            return ls
        city_div = city_url.find('div',attrs={'class':'listBox'})
        city_li = city_div.find_all('li')
        city_li_a = city_li[2].find('a')
        if city_li_a['href'] and city_li_a.text =='找小区' and city_li_a.text != '':
            urlx = city_li_a['href'].split('/housing')[0]
            page_city_qu = requests.get(city_li_a['href'].strip(), headers=self.headers, timeout=(3.05, 3.5))
            html_city_qu = page_city_qu.content.decode('gbk', errors='ignore')
            soup_city_qu = BeautifulSoup(html_city_qu, "html.parser")
            div_pq = soup_city_qu.find_all('div',attrs={'class':'sq-info mt10'})
            for div_pq_all in div_pq:
                pianqu_a = div_pq_all.find_all('a')
                for pianqu_all in pianqu_a:
                    if pianqu_all['href']:
                        quyu = urlx+pianqu_all['href']
                        ls.append(UrlBean(quyu, self.message('getpq'), param=pianqu_all.text, order=i_order))
        return ls

    #解析片区
    #@retries(100, delay=1, backoff=1, exceptions=(RequestException,))
    def getpq(self, urlbase):
        LOG.info('wwwsfcjcom %s 片区信息', urlbase.param)
        time.sleep(random()+2)
        r = requests.get(urlbase.url, headers=self.headers, timeout=(3.05, 3.5))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwlianjiacjcom %s 返回状态:%s', urlbase.url, r.status_code)
            return None
        ls = []
        i_order = urlbase.order[:-1]+'2'
        html_xiaoqu_ye = r.content.decode('gbk', errors='ignore')
        soup_xiaoqu_ye = BeautifulSoup(html_xiaoqu_ye, 'html.parser')
        try:
            yue = int(re.findall('<span class="txt">共(.*?)页</span></div>',html_xiaoqu_ye,re.S)[0])
            for j in range(yue):
                pageurl = r.request.url.split('_')
                pageurl[6] = str(j+1)
                call_page = '_'.join(pageurl)
                ls.append(UrlBean(call_page, self.message('getxq'), param=str(j+1), order=i_order))
        except Exception as e:
            LOG.error("%s%s", str(e), type(e))
        return ls

    #解析小区
    #@retries(100, delay=1, backoff=1, exceptions=(RequestException,))
    def getxq(self, urlbase):
        LOG.info('wwwsfcjcom获得 %s 小区信息', urlbase.param)
        time.sleep(random()+2)
        r = requests.get(urlbase.url, headers=self.headers, timeout=(3.05, 7.5))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwsfcjcom %s 返回状态:%s', urlbase.url, r.status_code)
            return None
        html_call = r.content.decode('gbk', errors='ignore')
        soup_call = BeautifulSoup(html_call, "html.parser")
        ls = []
        i_order = urlbase.order[:-1]+'3'
        xiaoqu_lite = soup_call.find('div',attrs={'class':'houseList'})
        xiaoqu_url = xiaoqu_lite.find_all('dt')
        for xiaoqu_all in xiaoqu_url:
            xiaoqu_a = xiaoqu_all.find('a')
            if xiaoqu_a:
                strUrl = xiaoqu_a['href'] if 'http' in xiaoqu_a['href'] else '%s%s' % ('/'.join(urlbase.url.split('/')[:3]), xiaoqu_a['href'])
                ls.append(UrlBean(strUrl, self.message('getpages'), param=xiaoqu_a.text, order=i_order))
        return ls

    #解析列表
    #@retries(100, delay=1, backoff=1, exceptions=(RequestException,))
    def getpages(self, urlbase):
        LOG.info('wwwsfcjcom获得 %s 成交列表信息', urlbase.param)
        time.sleep(random()+2)
        r = requests.get(urlbase.url, headers=self.headers, timeout=(3.05, 3.5))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwsfcjcom %s 返回状态:%s', urlbase.url, r.status_code)
            return None
        ls = []
        i_order = urlbase.order[:-1]+'4'
        html_xiaoqu = r.content.decode('gbk', errors='ignore')
        soup_xiaoqu = BeautifulSoup(html_xiaoqu, "html.parser")
        xiaoqu_div = soup_xiaoqu.find('div',attrs={'class':'plptinfo_list clearfix'})
        if xiaoqu_div is None:
            return ls
        d = {}
        xiaoqu_name = soup_xiaoqu.find('h1').find('a').text
        d['小区名称'] = xiaoqu_name
        d['小区链接'] = urlbase.url
        xiaoqu_ul = xiaoqu_div.find('ul')
        # print(xiaoqu_ul)
        #xiaoqu_ul.find('li', text=re.compile(r'所在区域'))

        # d['所属区域'] = xiaoqu_ul[0].text.replace("所在区域：",'').split(' ')[0]
        # d['建成年份'] = xiaoqu_ul[1].text.replace("建筑年代：",'')
        # d['楼盘物业类型'] = xiaoqu_ul[2].text.replace("物业类型：",'')
        # d['楼盘开发商'] = xiaoqu_ul[4].text.replace("开 发 商：",'')
        # d['楼盘绿化率'] = xiaoqu_ul[5].text.replace("绿 化 率：",'')
        # d['楼盘物业公司'] = xiaoqu_ul[7].text.replace("物业公司：",'')
        # d['楼盘物业费'] = xiaoqu_ul[8].text.replace("物 业 费：",'')
        try:
            d['所属区域'] = xiaoqu_ul.find('strong', text=re.compile(r'所在区域：')).next_sibling.split(' ')[0]
        except:pass
        try:
            d['建成年份'] = str(xiaoqu_ul.find('strong', text=re.compile(r'建筑年代：')).next_sibling)
        except:pass
        try:
            d['楼盘物业类型'] = str(xiaoqu_ul.find('strong', text=re.compile(r'物业类型：')).next_sibling)
        except:pass
        try:
            kfs = xiaoqu_ul.find('strong', text=re.compile(r'开 发 商：')).next_sibling
            d['楼盘开发商'] = str(kfs) if kfs else ''
        except:pass
        try:
            d['楼盘绿化率'] = str(xiaoqu_ul.find('strong', text=re.compile(r'绿 化 率：')).next_sibling)
        except:pass
        try:
            d['楼盘物业公司'] = str(xiaoqu_ul.find('strong', text=re.compile(r'物业公司：')).next_sibling)
        except:pass
        try:
            d['楼盘物业费'] = str(xiaoqu_ul.find('strong', text=re.compile(r'物 业 费：')).next_sibling)
        except:pass

        dz = soup_xiaoqu.find('div',attrs={'class':'ad_text'}).find_all('p')
        d['地址'] = dz[0].text
        d['城市'] = soup_xiaoqu.find('div',attrs={'class':'s2'}).find('div',attrs={'class':'s4Box'}).text
        try:
            chengjiao = re.findall('<p>历史总成交：<a href="(.*?)"><span class="bold">',html_xiaoqu,re.S)[0]
        except:
            chengjiao = xiaoqu_url_a
        if 'chengjiao' in chengjiao:
            strUrl = chengjiao if 'http' in chengjiao else '%s%s' % ('/'.join(urlbase.url.split('/')[:3], chengjiao))
            time.sleep(random()+2)
            page_chengjiao = requests.get(chengjiao, headers=self.headers, timeout=(3.05, 3.5))
            html_chengjiao = page_chengjiao.content.decode('gbk', errors='ignore')
            soup_chengjiao = BeautifulSoup(html_chengjiao, "html.parser")
            chengjiao_yeshu = soup_chengjiao.find('div',attrs={'class':'fanye gray6'})
            if chengjiao_yeshu is None:
                return ls
            if chengjiao_yeshu.text != '':
                ys_ls = re.findall('\d+',chengjiao_yeshu.text,re.S)
                #如果有页数
                if ys_ls:
                    t_page_1 = int(re.findall('\d+',chengjiao_yeshu.text,re.S)[-1])
                    for i in range(t_page_1):
                        urlxx = chengjiao + '-p1' + str(i+1) + '-t11/'
                        ls.append(UrlBean(urlxx, self.message('getitem'), param=dict(d), order=i_order))
        return ls

    #解析详细页面信息
    #@retries(100, delay=1, backoff=1, exceptions=(RequestException,))
    def getitem(self, urlbase):
        LOG.info('wwwsfcjcom获得%s成交详细信息', urlbase.url)
        t1 = time.time()
        time.sleep(random()+2)
        r = requests.get(urlbase.url, headers=self.headers, timeout=(3.05, 3.5))
        t2 = time.time()
        LOG.info('处理wwwsfcjcom请求getitem耗时:%f' % (t2-t1))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        #存储页面信息
        t1 = time.time()
        self.htmlwrite.save('%s\\%s\\%s' %(self.__class__.__name__, '真实成交', r.url.split('.')[0].split('/')[-1]), r.url, r.text)
        t2 = time.time()
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwsfcjcom %s 返回状态:%s', r.request.url, r.status_code)
            return
        t1 = time.time()
        html_xiangqing = r.content.decode('gbk', errors='ignore')
        soup_xiangqing = BeautifulSoup(html_xiangqing, "html.parser")
        li = soup_xiangqing.find('div', class_='cjjl').find_all('li')
        for li_all in li[1:]:
            d = dict(urlbase.param)
            span = li_all.find_all('span')
            if len(span) == 9:
                d['挂牌时间'] = span[0].text
                d['总价'] = span[1].getText(strip=True).replace('万','')
                d['单价'] = span[2].getText(strip=True).replace('元/㎡','')
                d['户型'] = span[3].getText(strip=True)
                try:
                    d['卧室数量'] = re.search('(\d*)室', d['户型']).group(1)
                except:pass
                try:
                    d['客厅数量'] = re.search('(\d*)厅', d['户型']).group(1)
                except:pass
                d['建筑面积'] = span[4].getText(strip=True).replace('㎡','')
                d['总层数'] = span[5].getText(strip=True).split('/')[1].replace('层','')
                d['当前层'] = span[5].getText(strip=True).split('/')[0].replace('层','')
                d['朝向'] = span[6].getText(strip=True).replace('向','')
                d['联系人'] = span[7].text
                d['信息来源'] = span[8].text
                if span[0].text !='成交日期' and span[1].text !='成交价' and span[2].text !='单价' and span[3].text !='户型' and span[4].text !='建筑面积' and span[5].text !='楼层' and span[6].text !='朝向' and span[7].text !='服务经纪人' and span[8].text !='来源':
                    d['RECMETAID'] = ''
                    d['题名'] = ''
                    d['来源链接'] = urlbase.url
                    # print(d['小区名称'] + '\t' + d['挂牌时间'] + '\t' + d['总价'] + '\t' + d['单价'] + '\t' + d['户型'] + '\t' + d['建筑面积'] + '\t' + d['当前层'] + '\t' + d['朝向'] + '\t' + d['联系人'] + '\t' + d['信息来源']+ '\n')
                    #d['小区链接'] = ''
                    d['楼栋名称'] = ''
                    d['使用面积'] = ''
                    d['产权性质'] = ''
                    d['装修情况'] = ''
                    d['卫生间数量'] = ''
                    d['厨房数量'] = ''
                    d['阳台数量'] = ''
                    d['房屋图片'] = ''
                    d['所属公司'] = ''
                    d['联系电话'] = ''
                    d['纬度'] = ''
                    d['经度'] = ''
                    d['备注'] = ''
                    d['预留字段'] = ''
                    d['房源编号'] = ''
                    d['发布时间'] = ''
                    d['住宅类别'] = ''
                    d['建筑类别'] = ''
                    d['配套设施'] = ''
                    d['估价链接'] = ''
                    d['租金链接'] = ''
                    d['房屋标签'] = ''
                    d['交通状况'] = ''
                    d['街景地图场景ID'] = ''
                    d['地图链接'] = ''
                    d['楼盘详情和所属HTML'] = ''
                    d['本月均价'] = ''
                    d['楼盘价格走势'] = ''
                    d['小区详情走势图链接'] = ''
                    d['经纪人链接'] = ''
                    d['经纪人图片链接'] = ''
                    d['小区成交历史链接'] = ''
                    d['行政区'] = ''
                    # x = format_str(d['RECMETAID'])+'\t'+format_str(d['题名'])+'\t'+format_str(d['来源链接'])+'\t'+format_str(d['小区名称'])+'\t'+d['所属区域'] +'\t'+ format_str(d['小区链接'])+'\t'+format_str(d['楼栋名称'])+'\t'+format_str(d['地址'])+'\t'+format_str(d['建成年份'])+'\t'+format_str(d['总层数'])+'\t'+format_str(d['当前层'])+'\t'+format_str(d['朝向'])+'\t'+format_str(d['建筑面积'])
                    # y = format_str(d['使用面积'])+'\t'+format_str(d['产权性质'])+'\t'+format_str(d['装修情况'])+'\t'+format_str(d['户型'])+'\t'+format_str(d['卧室数量'])+'\t'+format_str(d['客厅数量'])+'\t'+format_str(d['卫生间数量'])+'\t'+format_str(d['厨房数量'])+'\t'+format_str(d['阳台数量'])+'\t'+format_str(d['单价'])+'\t'+format_str(d['总价'])
                    # z = format_str(d['挂牌时间'])+'\t'+format_str(d['房屋图片'])+'\t'+format_str(d['信息来源'])+'\t'+format_str(d['联系人'])+'\t'+format_str(d['所属公司'])+'\t'+format_str(d['联系电话'])+'\t'+format_str(d['纬度'])+'\t'+format_str(d['经度'])+'\t'+format_str(d['备注'])+'\t'+format_str(d['预留字段'])+'\t'+format_str(d['房源编号'])
                    # w = format_str(d['发布时间'])+'\t'+format_str(d['住宅类别'])+'\t'+format_str(d['建筑类别'])+'\t'+format_str(d['配套设施'])+'\t'+format_str(d['估价链接'])+'\t'+format_str(d['租金链接'])+'\t'+format_str(d['房屋标签'])+'\t'+format_str(d['交通状况'])+'\t'+format_str(d['街景地图场景ID'])+'\t'+format_str(d['地图链接'])+'\t'+format_str(d['楼盘详情和所属HTML'])
                    # q = format_str(d['楼盘物业类型'])+'\t'+format_str(d['楼盘绿化率'])+'\t'+format_str(d['楼盘物业费'])+'\t'+format_str(d['楼盘物业公司'])+'\t'+format_str(d['楼盘开发商'])+'\t'+format_str(d['本月均价'])+'\t'+format_str(d['楼盘价格走势'])+'\t'+format_str(d['小区详情走势图链接'])+'\t'+format_str(d['经纪人链接'])+'\t'+format_str(d['经纪人图片链接'])+'\t'+format_str(d['小区成交历史链接'])+'\t'+format_str(d['城市'])+'\t'+format_str(d['行政区'])
                    # print(x+'\t'+y+'\t'+z+'\t'+w+'\t'+q)
                    # time.sleep(3)
                # with open('sf_cjsj.txt', 'a+', encoding='utf8') as f:
                #     f.write(x + '\t' + y + '\t' + z + '\t' + w + '\t' + q + '\n')
                #     f.flush()
                for meta in d:
                    d[meta] = format_str(d[meta])
                d['数据来源'] = 'sf'
                d['STR_ORDER'] = urlbase.order
                self.completionlr(d, metadatas)
                MySqlEx.savecj(d, metadatas)
        t2 = time.time()
        LOG.info('解析页面耗时:%f' % (t2-t1))

if __name__ == '__main__':
    sfcj = wwwsfcjcom()
    # for city in sfcj.default(UrlBase('http://fang.com/SoufunFamily.htm', 'wwwsfcjcom', order='1604270928')):
    #     for qy in sfcj.getqy(city)[:1]:
    #         for pq in sfcj.getpq(qy)[:2]:
    #             for xq in sfcj.getxq(pq)[:2]:
    #                 for item in sfcj.getpages(xq)[:2]:
    #                     sfcj.getitem(item)
    # ctiy = sfcj.default(UrlBase('http://fang.com/SoufunFamily.htm', 'wwwsfcjcom', order='1603070948'))[0]
    # qy = sfcj.getqy(ctiy)[0]
    # pq = sfcj.getpq(qy)[0]
    # xq = sfcj.getxq(pq)[0]
    for page in sfcj.getpages(UrlBean('http://xinshijiejiayuan.fang.com/', 'wwwsfcjcom#getpage', param='新世界家园小区网', order='1604270928')):
        sfcj.getitem(page)
    # xq = sfcj.getxq(UrlBean('http://esf.xm.fang.com/housing/_7221_0_0_0_0_2_0_0/', 'wwwsfcjcom#getxq', param={}, order='160307094801'))
    # sfcj.getpages(xq[0])
    # for page in sfcj.getpages(UrlBean('http://sdqygy.fang.com/office/', 'wwwsfcjcom#getitem', param={}, order='160307094801')):
    #     sfcj.getitem(page)