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
from requests.exceptions import RequestException
#解析中原地产真是成交数据
class wwwcentanetcom(ParserBase):
    headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36 LBBROWSER', 'Connection': 'keep-alive'}
    htmlwrite = HtmlFile()

    def __init__(self):
        super(wwwcentanetcom, self).__init__()

    #加载城市页面列表
    def default(self, urlbase):
        LOG.info('中原交易采集范围')
        citys = (("http://bj.centanet.com/chengjiao/g", 100), #北京 250页
                 ("http://cd.centanet.com/chengjiao/g", 60),
                 ("http://cq.centanet.com/chengjiao/g", 60),
                 ("http://nj.centanet.com/chengjiao/g", 35),
                 ("http://sh.centanet.com/chengjiao/g", 200), #250
                 ("http://sz.centanet.com/chengjiao/g", 100), #250
                 ("http://tj.centanet.com/chengjiao/g", 92))  #250
        i_order = urlbase.order+'0'
        ls = []
        for city in citys:
            for i in range(city[1]):
                ls.append(UrlBean("%s%d/" % (city[0], i+1), self.message('getpages'), order=i_order))
        return ls

    #解析城市二手房列表页
    #@retries(10, delay=1, backoff=1, exceptions=(RequestException))
    def getpages(self, urlbase):
        LOG.info('centanetgetpages获得城市%s成交列表信息', urlbase.url)
        r = requests.get(urlbase.url, headers=self.headers, timeout=(3.05, 5))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwcentanetcom %s 返回状态:%s', urlbase.url, r.status_code)
            return None
        i_order = urlbase.order+'1'
        ls = []
        #上海
        if 'http://sh.centanet.com' in urlbase.url:
            html = r.text
            soup = BeautifulSoup(html, 'html.parser') #lxml
            tatle = soup.find_all('tr',attrs={'class':'js_point_list'})
            for tr in tatle:
                d = {}  #定义结果集合
                tatle_td = tr.find_all('td')
                if len(tatle_td) == 8:
                    d['挂牌时间'] = tatle_td[0].text
                    # print(d['挂牌时间'])
                    XQ_name = tatle_td[1].find_all('span',attrs={'class':'js_map_animate'})
                    for name in XQ_name:
                        name_tatle = name.find('a')
                        d['小区名称'] = name_tatle.text
                        d['户型'] = tatle_td[2].getText(strip=True)
                        try:
                            d['卧室数量'] = re.search('(\d*)室', d['户型']).group(1)
                        except:pass
                        d['建筑面积'] = tatle_td[3].getText(strip=True).replace('平米', '')
                        d['总价'] = tatle_td[4].getText(strip=True).replace('万', '')
                        d['单价'] = tatle_td[5].getText(strip=True).replace('元/平', '')
                        d['联系人'] = tatle_td[6].text
                        CX_url = tatle_td[7].find('a')
                        d['城市'] = re.findall('<span class="yhtext">(.*?)</span><i class="icon-arrow"></i>',html,re.S)[0]
                        if CX_url['href']:
                            Cx_lint = "%s%s" % ('/'.join(r.url.split('/')[:3]), CX_url['href'])
                            #d['来源链接'] = Cx_lint
                            #page_lint = geturl(Cx_lint)
                            ls.append(UrlBean(Cx_lint, self.message('getitem'), key=Cx_lint, param=d, order=i_order))
        #其它城市
        else:
            html = re.findall(r'<table\s*class="table-record">[\s\S]*</table>', r.text)[0]
            soup = BeautifulSoup(html, 'html.parser') #lxml
            for tr in soup.find_all('tr'):
                d = {}  #定义结果集合
                tatle_td = tr.find_all('td')
                if len(tatle_td) == 6:
                    d['小区名称'] = tatle_td[0].text
                    try:
                        d['小区链接'] = '/'.join(r.url.split('/')[:3])+tatle_td[0].find('a')['href']
                    except:
                        d['小区链接'] = ''
                    d['挂牌时间'] = tatle_td[4].text
                    d['户型'] = tatle_td[1].text
                    d['朝向']=tatle_td[2].text.split('|')[0]
                    d['当前层']= tatle_td[2].text.split('|')[1]
                    d['建筑面积'] = tatle_td[3].text.replace('平', '')
                    d['总价'] = tatle_td[5].text.replace('万', '')
                    Cx_lint = '/'.join(r.url.split('/')[:3]) + tatle_td[5].find('a')['href']
                    #d['来源链接'] = '/'.join(r.url.split('/')[:3]) + tatle_td[5].find('a')['href']
                    ls.append(UrlBean(Cx_lint, self.message('getitem'), key=Cx_lint, param=d, order=i_order))
        return ls

    #解析详细页面信息
    #@retries(10, delay=1, backoff=1, exceptions=(RequestException))
    def getitem(self, urlbase):
        LOG.info('centanetgetitem获得成交%s详细信息', urlbase.url)
        t1 = time.time()
        r = requests.get(urlbase.url, headers=self.headers, timeout=(3.05, 5))
        t2 = time.time()
        LOG.info('处理centanetgetitem请求getitem耗时:%f' % (t2-t1))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        #存储页面信息
        t1 = time.time()
        self.htmlwrite.save('%s\\%s\\%s' %(self.__class__.__name__, '真实成交', r.url.split('.')[0].split('/')[-1]), r.url, r.text)
        t2 = time.time()
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwcentanetcom %s 返回状态:%s', r.request.url, r.status_code)
            return
        t1 = time.time()
        html_lint = r.content.decode('utf8', errors='ignore')
        soup_lint = BeautifulSoup(html_lint, 'html.parser') #lxml
        d = urlbase.param or {}
        d['来源链接'] = urlbase.url
        #上海
        if 'http://sh.centanet.com' in urlbase.url:
            louceng = soup_lint.find('h1',attrs={'style':'display: inline; font-weight: 400;'})
            louceng_span = louceng.find_all('span')
            # if len(louceng_span) == 5:
            #     try:
            #         if louceng_span[3].text.split('/')[0].strip() != "":
            #             d['当前层'] = louceng_span[3].text.split('/')[0]
            #     except:pass
            #     try:
            #         d['总层数'] = louceng_span[3].text.split('/')[1]
            #     except:pass
            # elif len(louceng_span) == 6:
            for span in louceng_span:
                if '层' in span.text:
                    try:
                        d['当前层'] = span.text.split('/')[0]
                    except:pass
                    try:
                        d['总层数'] = span.text.split('/')[1]
                    except:pass
                elif re.search(r'[东南西北]', span.text):
                    d['朝向'] = span.text
                elif '装' in span.text:
                    d['装修情况'] = span.text
            d['所属区域'] = re.findall('<span class="w_70 cGray">行&nbsp;&nbsp;政&nbsp;&nbsp;区：</span><p class="disinfo_r">(.*?)</a>',html_lint,re.S)[0]
            dr = re.compile(r'<[^>]+>',re.S)
            d['所属区域'] = re.sub(dr,'',d['所属区域'])
            d['地址'] = re.findall('<span class="w_70 cGray">地&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;址：</span>(.*?)</a>',html_lint,re.S)[0]
            d['地址'] = re.sub(dr,'',d['地址'])
            try:
                d['楼盘物业公司'] = re.findall('<span class="w_70 cGray">物业公司：</span><p class="disinfo_r">(.*?)</p>',html_lint,re.S)[0]
                d['楼盘开发商'] = re.findall('<span class="w_70 cGray">开&nbsp;&nbsp;发&nbsp;&nbsp;商：</span>(.*?)</p>',html_lint,re.S)[0]
                d['楼盘开发商'] = re.sub(dr,'',d['楼盘开发商'])
            except:
                d['楼盘物业公司'] = ''
                d['楼盘开发商'] = ''
            Xq_url = soup_lint.find('div',attrs={'class':'Mdetail_1'})
            Xq_url_lint = Xq_url.find('h2').find('a')
            if Xq_url_lint['href']:
                Xq_url_lint_1 = "%s%s" % ('/'.join(r.url.split('/')[:3]), Xq_url_lint['href'])
                d['小区链接'] = Xq_url_lint_1
                page_list = requests.get(Xq_url_lint_1, headers=self.headers, timeout=(3.05, 5))
                #page_list = geturl(Xq_url_lint_1)
                html_list = page_list.text
                soup_list = BeautifulSoup(html_list, 'html.parser')
                try:
                    d['本月均价'] = re.findall('<span class="f666 f12">均价</span><b class="cRed priceNub mr6"><span>￥</span>(.*?)</b>',html_list,re.S)[0]
                    d['建成年份'] = re.findall('<span class="f666">建造年代：</span><span class="f000">(.*?)年',html_list,re.S)[0]
                    d['楼盘物业类型'] = re.findall('<li class="halfline"><s class="fourword">物业类型：</s> <b class="fourword">(.*?)</b>',html_list,re.S)[0]
                    d['楼盘绿化率'] = re.findall('<li class="halfline"><s class="fourword">绿化率：</s> <b class="fourword">(.*?)</b>',html_list,re.S)[0]
                    d['楼盘物业费'] = re.findall('<li class="halfline"><s class="fourword">物业费：</s> <b class="fourword">(.*?)</b>',html_list,re.S)[0]
                except:
                    d['本月均价'] = ''
                    d['建成年份'] = ''
                    d['楼盘物业类型'] = ''
                    d['楼盘绿化率'] = ''
                    d['楼盘物业费'] = ''

                # x = format_str(d['RECMETAID'])+'\t'+format_str(d['题名'])+'\t'+format_str(d['来源链接'])+'\t'+format_str(d['小区名称'])+'\t'+format_str(d['所属区域'])+'\t'+format_str(d['小区链接'])+'\t'+format_str(d['楼栋名称'])+'\t'+format_str(d['地址'])+'\t'+format_str(d['建成年份'])+'\t'+format_str(d['总层数'])+'\t'+format_str(d['当前层'])+'\t'+format_str(d['朝向'])+'\t'+format_str(d['建筑面积'])
                # y = format_str(d['使用面积'])+'\t'+format_str(d['产权性质'])+'\t'+format_str(d['装修情况'])+'\t'+format_str(d['户型'])+'\t'+format_str(d['卧室数量'])+'\t'+format_str(d['客厅数量'])+'\t'+format_str(d['卫生间数量'])+'\t'+format_str(d['厨房数量'])+'\t'+format_str(d['阳台数量'])+'\t'+format_str(d['单价'])+'\t'+format_str(d['总价'])
                # z = format_str(d['挂牌时间'])+'\t'+format_str(d['房屋图片'])+'\t'+format_str(d['信息来源'])+'\t'+format_str(d['联系人'])+'\t'+format_str(d['所属公司'])+'\t'+format_str(d['联系电话'])+'\t'+format_str(d['纬度'])+'\t'+format_str(d['经度'])+'\t'+format_str(d['备注'])+'\t'+format_str(d['预留字段'])+'\t'+format_str(d['房源编号'])
                # w = format_str(d['发布时间'])+'\t'+format_str(d['住宅类别'])+'\t'+format_str(d['建筑类别'])+'\t'+format_str(d['配套设施'])+'\t'+format_str(d['估价链接'])+'\t'+format_str(d['租金链接'])+'\t'+format_str(d['房屋标签'])+'\t'+format_str(d['交通状况'])+'\t'+format_str(d['街景地图场景ID'])+'\t'+format_str(d['地图链接'])+'\t'+format_str(d['楼盘详情和所属HTML'])
                # q = format_str(d['楼盘物业类型'])+'\t'+format_str(d['楼盘绿化率'])+'\t'+format_str(d['楼盘物业费'])+'\t'+format_str(d['楼盘物业公司'])+'\t'+format_str(d['楼盘开发商'])+'\t'+format_str(d['本月均价'])+'\t'+format_str(d['楼盘价格走势'])+'\t'+format_str(d['小区详情走势图链接'])+'\t'+format_str(d['经纪人链接'])+'\t'+format_str(d['经纪人图片链接'])+'\t'+format_str(d['小区成交历史链接'])+'\t'+format_str(d['城市'])+'\t'+format_str(d['行政区'])
                for meta in d:
                    d[meta] = format_str(d[meta])
                # print(x+'\t'+y+'\t'+z+'\t'+w+'\t'+q)
                # with open('zy_1101_2016-02-14.txt', 'a+', encoding='utf8') as f:
                #     f.write(x+'\t'+y+'\t'+z+'\t'+w+'\t'+q+'\n')
                #     f.flush()
                d['数据来源'] = 'zy'
                d['STR_ORDER']=urlbase.order
                self.completionlr(d, metadatas)
                MySqlEx.savecj(d, metadatas)
        #其它
        else:
            try:
                d['题名'] = soup_lint.find('h5',attrs={'class':'f18 '}).text
            except:
                d['题名'] = ''
            huxing = soup_lint.find('ul',attrs={'class':'already_mid clearfix'}).find_all('p')
            if len(huxing) == 3:
                d['户型'] = huxing[0].text
            try:
                d['RECMETAID']=soup_lint.find('cite',attrs={'class':'f999 mr_10'}).text.split('：')[1]
            except:
                d['RECMETAID']= ''
            danjia = soup_lint.find('dd',attrs={'class':'fl mid'})
            danjia_p = danjia.find_all('p')
            if len(danjia_p) == 3:
                d['单价'] = danjia_p[2].text.split('：')[1].replace('元/平', '')
                d['备注'] = danjia_p[1].text.split('：')[1].replace('万', '')
                lianxiren = soup_lint.find('dd',attrs={'class':'last fl'})
                try:
                    zongcengshu = soup_lint.find('p',attrs={'class':'f16 tc f666 alreadyTxt'}).getText(strip=True)
                except:
                    zongcengshu = ''
                try:
                    if zongcengshu.split('/')[0] != "":
                        d['当前层'] = zongcengshu.split('/')[0]
                except:pass
                try:
                    d['总层数'] = zongcengshu.split('/')[1]
                except:pass
                try:
                    d['联系人'] = lianxiren.find('p').text
                except:pass
                try:
                    d['联系电话'] = re.findall('<span class="cOrange js_agent400" zvalue="\{mobile:\'(.*?)\' ,staffNo: \'',htmll,re.S)[0]
                except:pass
                quyu = soup_lint.find('div',attrs={'class':'fl breadcrumbs-area f000 '})
                quyu_a = quyu.find_all('a')
                if len(quyu_a) == 5:
                    d['行政区'] = quyu_a[2].text
                    d['所属区域'] = quyu_a[3].text
                    d['城市'] = soup_lint.find('title').text.split('-')[-1].replace("中原地产",'')
                    try:
                        pagell = requests.get(d['小区链接'], headers=self.headers, timeout=(3.05, 5))
                        htmlll = pagell.text
                        soup_xq = BeautifulSoup(htmlll, 'html.parser')
                        XQ = soup_xq.find('ul',attrs={'class':'combase_txt clearfix'}).find_all('li')
                        d['本月均价'] = XQ[0].find('span',attrs={'class':'cRed f20'}).text.replace('元/平', '')
                        d['楼盘物业类型'] = XQ[1].find('div',attrs={'class':'txt_r f666'}).text
                        d['建成年份'] = XQ[2].find('div',attrs={'class':'txt_r f666'}).text
                        d['楼盘物业费'] = XQ[3].find('div',attrs={'class':'txt_r f666'}).text
                        d['楼盘物业公司'] = XQ[4].find('div',attrs={'class':'txt_r f666'}).text
                        d['楼盘开发商'] = XQ[5].find('div',attrs={'class':'txt_r f666'}).text
                        d['楼盘绿化率'] = XQ[7].find('div',attrs={'class':'txt_r f666'}).text
                    except:
                        d['本月均价'] = ''
                        d['楼盘物业类型'] = ''
                        d['建成年份'] = ''
                        d['楼盘物业费'] = ''
                        d['楼盘物业公司'] = ''
                        d['楼盘开发商'] = ''
                        d['楼盘绿化率'] = ''
                    d['数据来源'] = 'zy'
                    d['STR_ORDER']=urlbase.order
                    self.completionlr(d, metadatas)
                    MySqlEx.savecj(d, metadatas)
        t2 = time.time()
        LOG.info('解析页面耗时:%f' % (t2-t1))

if __name__ == '__main__':
    centanet = wwwcentanetcom()
    for page in centanet.default(UrlBase('http://www.centanet.com', 'wwwcentanetcom',order='1603070948')):
        for item in centanet.getpages(page)[:5]:
            centanet.getitem(item)
    # page = centanet.default(UrlBase('http://www.centanet.com', 'wwwcentanetcom',order='1603070948'))
    # item = centanet.getpages(UrlBean('http://bj.centanet.com/chengjiao/g1', 'wwwcentanetcom#getpages', order='16030709480'))[0]
    # centanet.getitem(item)
    # for page in centanet.default(UrlBase('http://www.centanet.com', 'wwwcentanetcom',order='1603070948')):
    #     for item in centanet.getpages(page):
    #         centanet.getitem(item)
#     ls = ('http://sh.centanet.com/chengjiao/120831125107bb6cc8f5a36f41abeeb3.html',
# 'http://nj.centanet.com/chengjiao/f18b645ed5154829b545e3bf5122bb66.html',
# 'http://bj.centanet.com/chengjiao/160503100641f29a138933d905abe26c.html',
# 'http://tj.centanet.com/chengjiao/120511141106b56818b41339ec93b331.html',
# 'http://cd.centanet.com/chengjiao/13122117052085dab4c12e006f8aa263.html',
# 'http://cq.centanet.com/chengjiao/11010910032979d00fbb888cbf4421ca.html',
# 'http://sz.centanet.com/chengjiao/14102216595120d96f84ae6342eabfd3.html'
# )
#     for indx, l in enumerate(ls):
#         print(indx+1)
#         centanet.getitem(UrlBean(l, 'wwwcentanetcom#getitem', order='160307094801'))