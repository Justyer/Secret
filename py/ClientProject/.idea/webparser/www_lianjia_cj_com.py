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
    return s.replace("\r\n",'').replace("\n",'').replace(' ', '').replace("\t",'').replace("\r",'').replace('\xa0','').lstrip().replace('&nbsp;','')

import requests, re
from bs4 import BeautifulSoup, Tag
from requests.exceptions import RequestException
#链家登录
def login(username='13836126857', password='sa123456', session=None):
    if session is not None:
        session.close()
    s = requests.session()
    s.headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36 LBBROWSER', 'Connection': 'keep-alive'}
    r = s.get("http://bj.lianjia.com")
    r = s.get("https://passport.lianjia.com/cas/xd/api?name=passport-lianjia-com")
    r = s.get("https://passport.lianjia.com/cas/prelogin/loginTicket?")
    data = r.json()
    r = s.post("https://passport.lianjia.com/cas/login", data={"code":"", "verifycode":"",
                                                              "isajax":"true",
                                                              "lt":data["data"],
                                                              "service":"http://bj.lianjia.com/",
                                                              "username":username, "password":password})
    data = r.json()
    if data["success"]!=1:
        LOG.error("登录失败,返回数据!", data)
    else:
        r = s.get("http://login.lianjia.com/login/getUserInfo/", params={"service":"http://bj.lianjia.com/",
                                                                         "st":data["ticket"],
                                                                         "callback":"casback14591365488510"})
    LOG.info("登录成功!")
    return s

#解析中原地产真是成交数据
class wwwlianjiacjcom(ParserBase):
    headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36 LBBROWSER', 'Connection': 'keep-alive'}
    htmlwrite = HtmlFile()

    def __init__(self):
        super(wwwlianjiacjcom, self).__init__()
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
        LOG.info('链家交易采集范围')
        citys = (("http://bj.lianjia.com/chengjiao/pg", 100, "北京"), #北京 100页
                 ("http://cd.lianjia.com/chengjiao/pg", 100, "成都"),
                 ("http://dl.lianjia.com/chengjiao/pg", 100, "大连"),
                 ("http://hz.lianjia.com/chengjiao/pg", 100, "杭州"),
                 ("http://nj.lianjia.com/chengjiao/pg", 100, "南京"),
                 ("http://qd.lianjia.com/chengjiao/pg", 100, "青岛"),
                 ("http://sh.lianjia.com/chengjiao/d", 100, "上海"),
                 ("http://tj.lianjia.com/chengjiao/pg", 100, "天津"))
        i_order = urlbase.order+'0'
        ls = []
        for city in citys:
            for i in range(city[1]):
                ls.append(UrlBean("%s%d/" % (city[0], i+1), self.message('getpages'), param=city[2], order=i_order))
        return ls

    #解析城市二手房列表页
    def getpages(self, urlbase):
        LOG.info('wwwlianjiacjcom获得城市%s成交列表信息', urlbase.url)
        r = self.getSession().get(urlbase.url, headers=self.headers, timeout=(3.05, 1.5))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwlianjiacjcom %s 返回状态:%s', urlbase.url, r.status_code)
            return None
        html = r.content.decode('utf8', errors='ignore')
        soup = BeautifulSoup(html, 'html.parser') #lxml
        i_order = urlbase.order+'1'
        ls = []
        d = {}  #定义结果集合
        d['城市'] = urlbase.param
        list_ul = soup.find('ul', class_=re.compile(r'(clinch-list)|(listContent)'))
        list_li = list_ul.find_all('li')
        if len(list_li) <= 30:
            for list_li_s in list_li:
                list_div = list_li_s.find_all('div', class_=re.compile(r'(info-panel)|(info)'))
                for list_div_s in list_div:
                    # print(list_div_s)
                    list_h2 = list_div_s.find('a')
                    if list_h2:
                        if list_h2['href']:
                            list_div_l = list_div_s.find('div', class_=re.compile(r'(col-2)|(address)'))
                            if list_div_l is None:
                                print(1)
                            d['挂牌时间'] = list_div_l.find('div', class_=re.compile(r'(div-cun)|(dealDate)')).text
                            #page_list = requests.get(list_h2['href'])
                            strUrl = list_h2['href'] if 'http' in list_h2['href'] else '%s%s' % ('/'.join(urlbase.url.split('/')[:3]), list_h2['href'])
                            ls.append(UrlBean(strUrl, self.message('getitem'), key=strUrl, param=dict(d), order=i_order))
        return ls

    #解析详细页面信息
    #@retries(10, delay=1, backoff=1, exceptions=(RequestException))
    def getitem(self, urlbase):
        LOG.info('wwwlianjiacjcom获得城市%s成交详细信息', urlbase.url)
        time.sleep(random()+1)
        t1 = time.time()
        r = self.getSession().get(urlbase.url, headers=self.headers, timeout=(3.05, 1.5))
        t2 = time.time()
        LOG.info('处理wwwlianjiacjcom请求getitem耗时:%f' % (t2-t1))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        #存储页面信息
        t1 = time.time()
        self.htmlwrite.save('%s\\%s\\%s' %(self.__class__.__name__, '真实成交', r.url.split('.')[0].split('/')[-1]), r.url, r.text)
        t2 = time.time()
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwlianjiacjcom %s 返回状态:%s', r.request.url, r.status_code)
            return
        t1 = time.time()
        #如果返回二手房信息就直接跳过不采
        if 'ershoufang' in r.url:
            LOG.warning('成交变更为二手房信息,不采集,%s', r.url)
            return
        elif r.url.endswith('chengjiao/'):
            LOG.warning('成交信息已经不存在,%s', r.url)
            return
        html_list = r.content.decode('utf8', errors='ignore')
        soup_list = BeautifulSoup(html_list, 'html.parser')
        if '页面没有找到' in soup_list.find('title'):
            LOG.warning('成交信息已经不存在,%s', r.url)
            return
        d = urlbase.param
        d['来源链接'] = urlbase.url
        title = soup_list.find('h1')
        # 上海A1模板, 南京\天津 A模板或B模板 其它为A2模板
        # 默认模板A
        if title is not None:
            d['题名'] = soup_list.find('h1').text
            if 'http://sh.lianjia.com' in urlbase.url:
                #print('A1')
                soup_cont = soup_list.find('div', class_='content')
                try:
                    d['地址'] = soup_cont.find('p',class_='addrEllipsis').text
                except:
                    d['地址'] = ''
                try:
                    d['总价'] = soup_cont.find('div',class_='mainInfo bold').text.replace('万', '')
                except:pass
                try:
                    d['单价'] = soup_cont.find('td',text=re.compile('单价：')).find_next('td').text.replace('元/平', '')
                except:pass
                try:
                    d['户型'] = soup_cont.find('div',attrs={'class':'room'}).find('div',attrs={'class':'mainInfo'}).getText(strip=True)
                except:pass
                try:
                    d['卧室数量'] = re.search(r'(\d*)室', d['户型']).group(1)
                except:pass
                try:
                    d['客厅数量'] = re.search(r'(\d*)厅', d['户型']).group(1)
                except:pass

                lc = soup_cont.find('td', text=re.compile('楼层：')).find_next('td').getText(strip=True)
                d['总层数'] = re.search(r'([^层/]*)[层/]*共?(\d*)层', lc).group(2)
                d['当前层'] = re.search(r'([^层/]*)[层/]*共?(\d*)层', lc).group(1)
                try:
                    d['建筑面积'] = soup_cont.find('div',attrs={'class':'area'}).find('div',attrs={'class':'mainInfo'}).getText(strip=True).replace('平', '')
                except:pass
                try:
                    d['建成年份'] = re.sub('年建?','',soup_cont.find('td',text=re.compile('年代：')).find_next('td').getText(strip=True))
                except:pass
                try:
                    d['朝向'] = soup_cont.find('td',text=re.compile('朝向：')).find_next('td').getText(strip=True)
                except:pass
                try:
                    d['装修情况'] = soup_cont.find('td',text=re.compile('装修：')).find_next('td').getText(strip=True)
                except:pass
                #d['建筑类别'] = ''
                try:
                    strUrl = soup_cont.find('td',text=re.compile('小区：')).find_next('td').find('a')['href']
                    d['小区链接'] = strUrl if 'http' in strUrl else '%s%s' % ('/'.join(urlbase.url.split('/')[:3]), strUrl)
                except:
                    d['小区链接'] = ''
                try:
                    d['小区名称'] = soup_cont.find('td',text=re.compile('小区：')).find_next('td').find('a').getText(strip=True)
                except:
                    d['小区名称'] = ''
                try:
                    d['所属区域'] = soup_list.find('div', class_='fl l-txt').find_all('a')[2].getText(strip=True).replace('二手房成交价格', '')
                except:
                    d['所属区域'] = ''
                d['RECMETAID'] = soup_cont.find('span', class_='houseNum').getText(strip=True).replace('房源编号：', '')
                d['联系人'] = soup_cont.find('div', class_='brokerName').getText(strip=True)
                d['联系电话'] = soup_cont.find('div', class_='phone').getText(strip=True)
            else:
                #print('A2')
                try:
                    d['地址'] = soup_list.find('span',attrs={'class':'fang-subway-ex'}).text
                except:
                    d['地址'] = ''
                d['总价'] = (soup_list.find('span',attrs={'class':'love-money'})\
                             or soup_list.find('dt', text=re.compile(r'售价：?')).find_next(class_='ft-num')).text.replace('万', '')
                d['单价'] = (soup_list.find('p',attrs={'class':'info-item'})\
                             or soup_list.find('dt', text=re.compile(r'单价：?')).find_next('dd')).text.replace('元 / 平米','')
                if soup_list.find('span',attrs={'class':'first'}):
                    d['户型'] = soup_list.find('span',attrs={'class':'first'}).find('label').text
                else:
                    d['户型'] = soup_list.find('dt', text=re.compile(r'户型：?')).find_next('dd').text
                d['卧室数量'] = re.search(r'(\d*)室', d['户型']).group(1)
                d['客厅数量'] = re.search(r'(\d*)厅', d['户型']).group(1)

                key = soup_list.find('div',attrs={'class':'info-box'})
                key_span = key.find_all('span')
                if len(key_span) == 3 :
                    lc = key_span[0].text.split('厅')[1]
                    try:
                        d['总层数'] = re.search(r'([^层(（]*)[层(（]*共(\d*)层\)', lc).group(2)
                    except:pass
                    try:
                        d['当前层'] = re.search(r'([^层(（]*)[层(（]*共(\d*)层\)', lc).group(1)
                    except:
                        d['当前层'] = lc
                    d['建筑面积'] = key_span[1].find('label').text.replace('平米', '')
                    d['建成年份'] = key_span[1].text.split('米')[1].split('年')[0]
                    d['朝向'] = key_span[2].find('label').text
                    d['建筑类别'] = key_span[2].text.replace('东','').replace('南','').replace('西','').replace('北','')
                else:
                    lc = soup_list.find('dt', text=re.compile(r'楼层：?')).find_next('dd').text
                    try:
                        d['总层数'] = re.search(r'([^层(（]*)[层(（]*共(\d*)层\)', lc).group(2)
                    except:pass
                    try:
                        d['当前层'] = re.search(r'([^层(（]*)[层(（]*共(\d*)层\)', lc).group(1)
                    except:
                        d['当前层'] = lc
                    d['建筑面积'] = soup_list.find('dt', text=re.compile(r'售价：?')).find_next('i').text.replace('㎡', '')
                    try:
                        d['建成年份'] = re.search(r'/span>([^<]*?)</dd', str(soup_list.find('dt', text=re.compile(r'小区：?')).find_next('dd'))).group(1).replace('年', '')
                    except:pass
                    d['朝向'] = soup_list.find('dt', text=re.compile(r'朝向：?')).find_next('dd').text

                xiaoqu_url = soup_list.find('p',attrs={'class':'info-item01'}) \
                                or soup_list.find('dt', text=re.compile(r'小区：?')).find_next('dd')
                xq_url = xiaoqu_url.find('a')
                if xq_url['href']:
                    d['小区链接'] = xq_url['href'] if 'http' in xq_url['href'] else '/'.join(urlbase.url.split('/')[:3])+xq_url['href']
                    d['小区名称'] = xq_url.text
                    if soup_list.find('p',attrs={'class':'info-item01'}):
                        d['所属区域'] = soup_list.find('p',attrs={'class':'info-item01'}).find('span').find('a').text
                    elif soup_list.find(attrs={'data-el':'district'}):
                        d['所属区域'] = soup_list.find(attrs={'data-el':'district'}).text
                    if soup_list.find('p',attrs={'class':'info-item02'}):
                        d['RECMETAID']= soup_list.find('p',attrs={'class':'info-item02'}).find('span').text.replace('房源编号：','')
                    elif soup_list.find('div', class_='iinfo'):
                        d['RECMETAID']= soup_list.find('div', class_='iinfo').find('span', text=re.compile(r'房源编号：?')).find_next('span').text
                    if soup_list.find('p',attrs={'class':'name'}):
                        d['联系人']=soup_list.find('p',attrs={'class':'name'}).find('a').text
                    elif soup_list.find('p', class_='p-01'):
                        d['联系人']=soup_list.find('p', class_='p-01').find('a').text
                    if soup_list.find('p',attrs={'class':'tel'}):
                        d['联系电话']=soup_list.find('p',attrs={'class':'tel'}).text
                    elif soup_list.find('div', class_='contact-panel'):
                        d['联系电话']=soup_list.find('div', class_='contact-panel').text

        # 模板B
        else:
            #print('B')
            d['题名'] = str(soup_list.find('div', class_='house-title').div.contents[0])
            try:
                d['地址'] = soup_list.find('div',attrs={'class':'info fr'}).find('div',class_='tag').text
            except:
                d['地址'] = ''
            price = soup_list.find('div', class_='info fr').find('div', class_='price').getText(strip=True)
            d['总价'] = re.search(r'(\d+\.?\d*)万', price).group(1)
            d['单价'] = re.search(r'(\d+\.?\d*)元/平米', price).group(1)
            d['户型'] = soup_list.find('div', class_='msg').find('span', class_='sp01').label.getText(strip=True)
            d['卧室数量'] = re.search(r'(\d*)室', d['户型']).group(1)
            d['客厅数量'] = re.search(r'(\d*)厅', d['户型']).group(1)

            lc = str(soup_list.find('div', class_='msg').find('span', class_='sp01').label.nextSibling)
            d['总层数'] = re.search(r'([^层(（]*)[层(（]*共(\d*)层\)', lc).group(2)
            d['当前层'] = re.search(r'([^层(（]*)[层(（]*共(\d*)层\)', lc).group(1)
            d['朝向'] = soup_list.find('div', class_='msg').find('span', class_='sp02').label.getText(strip=True)
            d['建筑面积'] = soup_list.find('div', class_='msg').find('span', class_='sp03').label.getText(strip=True).replace('平米', '')
            ss = str(soup_list.find('div', class_='msg').find('span', class_='sp03').label.nextSibling)
            d['建成年份'] = ss.split('年建')[0]
            d['建筑类别'] = ss.split('年建')[1]

            pinfo = soup_list.find('div', class_='info fr').p
            xiaoqu_url = soup_list.find('div', class_='info fr').p.find('a', class_='name')
            d['小区链接'] = xiaoqu_url['href'] if 'http' in xiaoqu_url['href'] else '%s%s' % ('/'.join(urlbase.url.split('/')[:3]), xiaoqu_url['href'])
            d['小区名称'] = xiaoqu_url.text
            d['所属区域'] = pinfo.find_all('a')[1].text
            d['RECMETAID'] = soup_list.find('span', class_='house-code').getText(strip=True).split('：')[1]
            d['联系人'] = soup_list.find('div',class_='agent').find('div',class_='fr').contents[0].text
            d['联系电话'] = soup_list.find('div',class_='agent').find('div',class_='fr').find('div',class_='tel').getText(strip=True)
        d['行政区']=d['所属区域']
        # x = format_str(d['RECMETAID'])+'\t'+format_str(d['题名'])+'\t'+format_str(d['来源链接'])+'\t'+format_str(d['小区名称'])+'\t'+d['所属区域'] +'\t'+ format_str(d['小区链接'])+'\t'+format_str(d['楼栋名称'])+'\t'+format_str(d['地址'])+'\t'+format_str(d['建成年份'])+'\t'+format_str(d['总层数'])+'\t'+format_str(d['当前层'])+'\t'+format_str(d['朝向'])+'\t'+format_str(d['建筑面积'])
        # y = format_str(d['使用面积'])+'\t'+format_str(d['产权性质'])+'\t'+format_str(d['装修情况'])+'\t'+format_str(d['户型'])+'\t'+format_str(d['卧室数量'])+'\t'+format_str(d['客厅数量'])+'\t'+format_str(d['卫生间数量'])+'\t'+format_str(d['厨房数量'])+'\t'+format_str(d['阳台数量'])+'\t'+format_str(d['单价'])+'\t'+format_str(d['总价'])
        # z = format_str(d['挂牌时间'])+'\t'+format_str(d['房屋图片'])+'\t'+format_str(d['信息来源'])+'\t'+format_str(d['联系人'])+'\t'+format_str(d['所属公司'])+'\t'+format_str(d['联系电话'])+'\t'+format_str(d['纬度'])+'\t'+format_str(d['经度'])+'\t'+format_str(d['备注'])+'\t'+format_str(d['预留字段'])+'\t'+format_str(d['房源编号'])
        # w = format_str(d['发布时间'])+'\t'+format_str(d['住宅类别'])+'\t'+format_str(d['建筑类别'])+'\t'+format_str(d['配套设施'])+'\t'+format_str(d['估价链接'])+'\t'+format_str(d['租金链接'])+'\t'+format_str(d['房屋标签'])+'\t'+format_str(d['交通状况'])+'\t'+format_str(d['街景地图场景ID'])+'\t'+format_str(d['地图链接'])+'\t'+format_str(d['楼盘详情和所属HTML'])
        # q = format_str(d['楼盘物业类型'])+'\t'+format_str(d['楼盘绿化率'])+'\t'+format_str(d['楼盘物业费'])+'\t'+format_str(d['楼盘物业公司'])+'\t'+format_str(d['楼盘开发商'])+'\t'+format_str(d['本月均价'])+'\t'+format_str(d['楼盘价格走势'])+'\t'+format_str(d['小区详情走势图链接'])+'\t'+format_str(d['经纪人链接'])+'\t'+format_str(d['经纪人图片链接'])+'\t'+format_str(d['小区成交历史链接'])+'\t'+format_str(d['城市'])+'\t'+format_str(d['行政区'])
        # print(x+'\t'+y+'\t'+z+'\t'+w+'\t'+q)
        # with open('lj_1101.txt', 'a+', encoding='utf8') as f:
        #     f.write(x + '\t' + y + '\t' + z + '\t' + w + '\t' + q + '\n')
        #     f.flush()
        # print(format_str(d['题名']) + '\t' + format_str(d['建筑类别']) + '\t' + format_str(d['建成年份']) + '\t' + format_str(d['建筑面积']) + '\t' + format_str(d['总楼层']) + '\t' + format_str(d['户型']) + '\t' + format_str(d['单价']) + '\t' + format_str(d['总价']) + '\t' + format_str(d['地址']) + '\t' + format_str(d['挂牌时间']) + '\t' + format_str(d['小区名称']) + '\t' + format_str(d['小区链接']) + '\t' + format_str(d['来源链接']) + '\t' + loginurl + '\n')
        for meta in d:
            d[meta] = format_str(d[meta])
        d['数据来源'] = 'lj'
        d['STR_ORDER'] = urlbase.order
        self.completionlr(d, metadatas)
        MySqlEx.savecj(d, metadatas)
        t2 = time.time()
        LOG.info('解析页面耗时:%f' % (t2-t1))

if __name__ == '__main__':
    lianjia = wwwlianjiacjcom()
    # for page in lianjia.default(UrlBase('http://www.lianjia.com', 'wwwlianjiacjcom', order='1603070948')):
    #     for item in lianjia.getpages(page):
    #         lianjia.getitem(item)
    #for i in range(100):
    #   print(len(lianjia.getpages(UrlBean('http://tj.lianjia.com/chengjiao/pg%d/' % (i+1), 'wwwlianjiacjcom#getitem', param={}, order='160307094801'))))
    lianjia.getitem(UrlBean('http://sh.lianjia.com/chengjiao/sh1183409.html', 'wwwlianjiacjcom#getitem', param={}, order='160307094801'))
    # with open("D:\\data\\lj.tsv", "r", encoding='gbk') as f:
    #     for idx, line in enumerate(f.readlines()):
    #         if idx+1<33518:
    #             continue
    #         print("\n\n", idx+1, "\n", line.strip())
    #         lianjia.getitem(UrlBean(line.strip(), 'wwwlianjiacjcom#getitem', param={}, order='160307094801'))