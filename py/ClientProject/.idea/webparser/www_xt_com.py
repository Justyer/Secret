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

LOG=logging.getLogger()
LOG.handlers[0].setLevel(logging.INFO)
LOG.handlers[1].setLevel(logging.INFO)

################################
# metadatas = ('题名','来源链接','小区名称','所属区域','小区链接','楼栋名称','地址','建成年份',                  #7
#             '总楼层','当前层','朝向','建筑面积','使用面积','产权性质','装修情况','户型','卧室数量',            #16
#             '客厅数量','卫生间数量','厨房数量','阳台数量','单价','总价','挂牌时间','房屋图片','信息来源',      #25
#             '联系人','经纪公司','电话号码','纬度','经度','发布时间','住宅类别','建筑类别','配套设施','交通状况', #35
#             '楼盘物业类型','楼盘绿化率','楼盘物业费','数据来源','城市','行政区','str_order')                    #42

metadatas = ('信息来源','城市','行政区','片区','来源链接','题名','小区名称','小区链接','地址','建成年份','房龄',                     #10
             '楼层','总楼层','当前层','朝向','建筑面积','使用面积','户型','卧室数量','客厅数量','卫生间数量',                        #20
             '厨房数量','阳台数量','总价','单价','本月均价','小区开盘单价','住宅类别','产权性质','装修情况','建筑类别',               #30
             '楼盘物业类型','小区简介','联系人','联系人链接','经纪公司','门店','电话号码','服务商圈','注册时间','经纪公司房源编号',    #40
             '发布时间','小区总户数','小区总建筑面积','容积率','小区总停车位','开发商','交通状况','配套设施','楼盘绿化率','物业公司',  #50
             '楼盘物业费','土地使用年限','入住率','学校','地上层数','花园面积','地下室面积','车库数量','车位数量','厅结构',           #60
             '导航','房屋图片','纬度','经度','str_order','数据来源')                                                                                    #65

import requests, re
from bs4 import BeautifulSoup, Tag
#from requests.exceptions import RequestException
#解析赶集网站
class wwwxtcom(ParserBase):
    headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36 LBBROWSER', 'Connection': 'keep-alive'}
    htmlwrite = HtmlFile()

    def __init__(self):
        super(wwwxtcom, self).__init__()

    def default(self, urlbase):
        LOG.info('禧泰默认方法获得城市列表!')
        r = requests.get(urlbase.url,headers=self.headers, timeout=(3.05, 3.5))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwxtcom %s 返回状态:%s', urlbase.url, r.status_code)
            return None
        soup = BeautifulSoup(r.content.decode('utf8'), 'html.parser') #lxml
        citys = soup.find('div', class_='col_detail').find_all('a', class_='fz_12')

        list = []
        i_count = 1
        i_order = urlbase.order+'0'
        t_20 = ('北京','上海')
        t_5 = ('广州')
        t_1 = ('深圳','成都')
        for i in citys:
            #if i.text not in ('北京', '上海', '广州', '深圳'): continue
            if i.text in t_20:
                i_count = 1
                while i_count <= 20:
                    list.append(UrlBean(i['href']+'/forsale/ob9-pg'+str(i_count)+'/', self.message('getpages'), param=i_count, headers=i.text, order=i_order))
                    LOG.info('获得城市%s页面信息%s', i.text, i['href']+'/forsale/ob9-pg'+str(i_count)+'/')
                    i_count += 1
            elif i.text in t_5:
                i_count = 1
                while i_count <= 5:
                    list.append(UrlBean(i['href']+'/forsale/ob9-pg'+str(i_count)+'/', self.message('getpages'), param=i_count, headers=i.text, order=i_order))
                    LOG.info('获得城市%s页面信息%s', i.text, i['href']+'/forsale/ob9-pg'+str(i_count)+'/')
                    i_count += 1
            elif i.text in t_1:
                list.append(UrlBean(i['href']+'/forsale/ob9/', self.message('getpages'), param=i_count, headers=i.text, order=i_order))
                LOG.info('获得城市%s页面信息%s', i.text, i['href']+'/forsale/ob9/')
        for i in range(1,21):
            list.append(UrlBean('http://bj.cityhouse.cn/forsale/ob9-pg'+str(i)+'/', self.message('getpages'), param=i, headers='北京', order=i_order))
            LOG.info('获得城市 北京 页面信息%s', 'http://bj.cityhouse.cn/forsale/ob9-pg'+str(i)+'/')
            list.append(UrlBean('http://sh.cityhouse.cn/forsale/ob9-pg'+str(i)+'/', self.message('getpages'), param=i, headers='上海', order=i_order))
            LOG.info('获得城市 上海 页面信息%s', 'http://sh.cityhouse.cn/forsale/ob9-pg'+str(i)+'/')
        return list

    #解析城市二手房列表页
    def getpages(self, urlbase):
        LOG.info('xtgetpages获得城市%s二手房列表信息', urlbase.url)
        time.sleep(1)
        r = requests.get(urlbase.url,headers=self.headers, timeout=(3.05, 3.5))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwxtcom %s 返回状态:%s', urlbase.url, r.status_code)
            return None
        soup = BeautifulSoup(r.content.decode('utf8','ignore'), 'html.parser') #lxml
        items = soup.find_all('h4')
        list = []
        itemIndex = 1
        i_order = urlbase.order+'1'
        host = '/'.join(r.url.split('/')[:3])
        for item in items:
            sUrl = host + item.findChild('a')['href']
            list.append(UrlBean(sUrl, self.message('getitem'), key=sUrl, param=urlbase.headers, order=i_order))
            LOG.debug('%s第%d页%d项' % (urlbase.headers, urlbase.param, itemIndex))
            itemIndex += 1
        return list;

    #解析详细页面信息
    #@retries(10, delay=1, backoff=1, exceptions=(RequestException))
    def getitem(self, urlbase):
        LOG.info('xtgetinfo获得城市%s挂牌详细信息', urlbase.url)
        time.sleep(1)
        t1 = time.time()
        r = requests.get(urlbase.url,headers=self.headers, timeout=(3.05, 3.5))
        t2 = time.time()
        LOG.info('处理xt请求getitem耗时:%f' % (t2-t1))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        #存储页面信息
        t1 = time.time()
        self.htmlwrite.save('%s\\%s\\%s' %(self.__class__.__name__, '二手房', urlbase.param), r.url, r.text)
        t2 = time.time()
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwxtcom %s 返回状态:%s', r.request.url, r.status_code)
            return
        t1 = time.time()
        reText = r.text
        soup = BeautifulSoup(reText, 'html.parser') #lxml
        lr = {}
        ###############################################################################################################
        def _strip(str_info):
            return str_info.strip().replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '')
        try:
            lr[metadatas[5]] = soup.find('h1').text
        except:
            lr[metadatas[5]]= ''

        lr[metadatas[4]] = r.url

        try:
            name = soup.find('ul',attrs={'class':'assess-ul mt20'}).find_all('li')           # 找到属性是class:assess-ul mt20 的ul标签,并找到子标签 li
            lr[metadatas[6]] = _strip(name[0].text).replace('小区：','').replace('地标：','').replace('位置：','')
        except:
            lr[metadatas[6]] = ''
        try:
            area = soup.find('a',attrs={'id':'fyt_district'}).text
            lr[metadatas[2]] = _strip(area)
        except:
            lr[metadatas[2]]=''

        try:
            lr[metadatas[8]]=soup.find('div',class_='su_tit',text=re.compile(r'位置：')).find_next('div').span.getText(strip=True)
        except:pass

        try:                                                  # 有的二手房没有小区有地标,地标意思与小区相近但是却没有链接
            lr[metadatas[7]] = '/'.join(r.url.split('/')[:3])+name[0].findChild('a')['href']
        except:
            lr[metadatas[7]] = ''

        try:
            ld_name = soup.find('div',attrs={'class':'crumbs'})
            lr[metadatas[61]] = _strip(ld_name.text)
        except:
            lr[metadatas[61]] = ''

        details = soup.find('div',attrs={'class':'cont h-parameters clearfix'})      #详情总列表

        try:
            details_dd = details.find_all('dd')
            lr[metadatas[9]] = _strip(details_dd[5].text).replace('年', '')
        except:
            lr[metadatas[9]] = ''

        floor = details_dd[2]   #楼层
        lr[metadatas[11]] = _strip(floor.text)
        z_floor = re.findall('共(.*?)层',str(floor),re.S)                             #正则  总楼层
        try:
            lr[metadatas[12]] = z_floor[0]
        except:
            lr[metadatas[12]] = ''
        dq_floor = re.findall('<dd>([^共]*?)[/<]',str(floor),re.S)
        try:#正则  当前层
            lr[metadatas[13]] =  _strip(dq_floor[0]).replace('层','')
        except:
            lr[metadatas[13]] = ''
        lr[metadatas[14]] = details_dd[3].text

        try:
            aera = re.findall('<span id="fyt_bldgarea">(.*?)</span>',reText,re.S)            #正则建筑面积
            lr[metadatas[15]] = _strip(aera[0]).replace('㎡','')
        except:
            lr[metadatas[15]] = ''

        try:
            lr[metadatas[28]] = details_dd[6].text
        except:
            lr[metadatas[28]] = ''

        try:
            lr[metadatas[29]] = details_dd[4].text
        except:
            lr[metadatas[29]] = ''

        try:
            first = re.findall('<li class="first">(.*?)</li>',reText,re.S)
            mr = re.findall('<span class="mr"(.*?)</span>',str(first),re.S)                #正则户型
            lr[metadatas[17]] = _strip(mr[0]).replace('>','')                              #户型不规则   下面数据只能用try
        except:
            lr[metadatas[17]] = ''

        try:
            room = re.findall('>(.*?)室',str(mr),re.S)
            lr[metadatas[18]] = room[0]
        except:
            lr[metadatas[18]] = ''
        try:
            living = re.findall('室(.*?)厅',str(mr),re.S)
            lr[metadatas[19]] =living[0]
        except:
            lr[metadatas[19]] = ''
        try:
            kitchen = re.findall('厅(.*?)厨',str(mr),re.S)
            lr[metadatas[21]] =kitchen[0]
        except:
            lr[metadatas[21]] = ''
        try:
            wc = re.findall('厨(.*?)卫',str(mr),re.S) or re.findall('厅(.*?)卫',str(mr),re.S)
            lr[metadatas[20]] =wc[0]
        except:
            lr[metadatas[20]] = ''

        try:
            u_price = re.findall('<span id="fyt_price" >(.*?)</span>',reText,re.S)
            lr[metadatas[24]] =u_price[0].replace(',','')
        except:
            lr[metadatas[24]] = ''
        try:
            t_price = re.findall('<span class="n">(.*?)</span>',reText,re.S)
            lr[metadatas[23]] =t_price[0].replace(',','')
        except:
            lr[metadatas[23]] = ''
        try:
            j_price = re.findall('</span>本月均价：<span class="red">(.*?)</span>',reText,re.S)
            lr[metadatas[25]] =j_price[0].replace(',','')
        except:
            lr[metadatas[25]] = ''

        try:
            lr[metadatas[41]] = _strip(details_dd[8].text)
        except:
            lr[metadatas[41]] = ''
        lr[metadatas[66]] = 'xt'
        lr[metadatas[0]]  = 's00000xt'

        try:
            phone = soup.find('span',attrs={'class':'numb'})
            pstr = phone.text
            if phone.find('script'):
                try:
                    rphone = requests.get('/'.join(urlbase.url.split('/')[:3])+phone.find('script')['src'], headers=self.headers, timeout=(3.05, 3.5))
                    pstr = re.search(r"'([^']*)", rphone.text).group(1)
                except:pass
            lr[metadatas[37]] = re.sub('\s+', ';', _strip(pstr).strip())
        except:
            lr[metadatas[37]] = ''
        try:
            habasex= re.findall('var habasex=(.*?);',reText,re.S)
            lr[metadatas[64]] = habasex[0]
        except:
            lr[metadatas[64]] = ''
        try:
            habasey= re.findall('var habasey=(.*?);',reText,re.S)
            lr[metadatas[63]] = habasey[0]
        except:
            lr[metadatas[63]] = ''

        lr[metadatas[27]] = _strip(details_dd[1].text)

        try:
            traffic = re.findall('<ul class="fz12 bus_xx">(.*?)</ul>',reText,re.S)
            dr = re.compile(r'<[^>]+>',re.S)
            dr_traffic = dr.sub('',traffic[0])
            lr[metadatas[47]] = _strip(dr_traffic).replace('&nbsp;','')
        except:
            lr[metadatas[47]] = ''

        try:
            lr[metadatas[48]] = soup.find('div', class_='su_tit', text=re.compile('附属设施：')).find_next('div').getText(strip=True)
        except:pass

        try:
            wylx = re.findall('物业类型：</dt>(.*?)</span>',reText,re.S)
            dr = re.compile(r'<[^>]+>',re.S)
            dr_wylx = dr.sub('',wylx[0])
            lr[metadatas[31]] = _strip(dr_wylx)
        except:
            lr[metadatas[31]] = ''

        try:
            green = re.findall('绿化率：</dt>(.*?)</span>',reText,re.S)
            dr = re.compile(r'<[^>]+>',re.S)
            dr_green = dr.sub('',green[0])
            lr[metadatas[49]] = _strip(dr_green)
        except:
            lr[metadatas[49]] = ''

        try:
            city = ld_name.find_all('a')
            lr[metadatas[1]] = _strip(city[1].text).replace('二手房','')
        except:
            lr[metadatas[1]] = ''

        comp = soup.find('div', class_='company')
        #先找经纪人模块
        if comp:
            #经纪公司
            try:
                lr[metadatas[35]] = comp.find('a').getText(strip=True)
            except:
                lr[metadatas[35]] = ''

            #联系人链接
            try:
                if comp:
                    if comp.find('a'):
                        lr[metadatas[34]] = comp.find('a')['href']
            except:
                lr[metadatas[34]] = ''

            #联系人
            try:
                if lr[metadatas[34]] and comp:
                    strUrl = lr[metadatas[34]] if 'http' in lr[metadatas[34]].lower() else '/'.join(r.request.url.split('/')[:3]) + lr[metadatas[34]]
                    lr[metadatas[34]] = strUrl
                    rjjr = requests.get(strUrl, headers=self.headers, timeout=(3.05, 3.5))
                    jjr_soup = BeautifulSoup(rjjr.content.decode('utf8'), 'html.parser') #lxml
                    lr[metadatas[33]] = jjr_soup.find('div', class_='shop-broker-list').find('dd').p.getText(strip=True)
            except:
                lr[metadatas[33]] = ''
        else:
            #联系人
            try:
                l_name = re.findall('<ul class="assess-ul">(.*?)</ul>',reText,re.S)
                dr = re.compile(r'<[^>]+>',re.S)
                link_name = dr.sub('',l_name[0])
                lr[metadatas[33]] = _strip(link_name).replace('联系人：','').replace('（经纪人）','')
            except:
                lr[metadatas[33]] = ''

            #联系人链接
            try:
                lr[metadatas[34]] = soup.find('div', class_='su_tit', text=re.compile('联系人：')).find_next('div', class_='su_con').find('a')['href']
                if not lr[metadatas[34]].lower().startswith('http'):
                    lr[metadatas[34]] = '%s%s' % ('/'.join(urlbase.url.split('/')[:3]), lr[metadatas[34]])
                rjjr = requests.get(lr[metadatas[34]], headers=self.headers, timeout=(3.05, 3.5))
                jjr_soup = BeautifulSoup(rjjr.content.decode('utf8'), 'html.parser') #lxml
                for li in jjr_soup.find('ul', class_='fl jjr_xx').find_all('li'):
                    if '所属公司' in li.getText(strip=True):
                        lr[metadatas[35]] = li.getText(strip=True).replace('所属公司：', '')
                        break
            except:
                lr[metadatas[34]] = ''

        lr[metadatas[65]] = urlbase.order if urlbase.order is not None else ''

        lr = self.completionlr(lr,metadatas)
        ###############################################################################################################
        t2 = time.time()
        LOG.info('解析页面耗时:%f' % (t2-t1))
        #将分析的信息写入数据库
        #www58com.mysql.save(lr, metadatas)
        self.completionlr(lr, metadatas)
        MySqlEx.save(lr, metadatas)

    #def getinfo(self, urlbase):
        #LOG.info('58getinfo获得%s挂牌详细信息' , urlbase.url)


if __name__ == '__main__':
    wxt = wwwxtcom()
    #print(len(wxt.default(UrlBase('http://www.cityhouse.cn/city.html', 'wwwxtcom',order='123'))))
    # wxt.getpages(UrlBean('http://gz.cityhouse.cn/forsale/ob9-pg5/', 'wwwxtcom#getitem', param=10, headers='哈尔滨',order='123'))
    wxt.getitem(UrlBean('http://ls.cityhouse.cn/forsale/0019374514321.html', 'wwwxtcom#getitem', param=9, headers='哈尔滨',order='123456'))
    wxt.getitem(UrlBean('http://aq.cityhouse.cn/forsale/0002346426811.html', 'wwwxtcom#getitem', param=9, headers='哈尔滨',order='123456'))

    ls = ('http://bj.cityhouse.cn/forsale/0062351094822.html',
'http://fushun.cityhouse.cn/forsale/0007992706431.html',
'http://sh.cityhouse.cn/forsale/0072944691543.html',
'http://wn.cityhouse.cn/forsale/0007736866487.html',
'http://ms.cityhouse.cn/forsale/0078514270255.html',
'http://sh.cityhouse.cn/forsale/0072944416196.html',
'http://sh.cityhouse.cn/forsale/0072946011983.html',
'http://cj.cityhouse.cn/forsale/0030621339525.html',
'http://zz.cityhouse.cn/forsale/0015831434327.html',
'http://bj.cityhouse.cn/forsale/0062351096912.html')

    for l in ls:
        wxt.getitem(UrlBean(l, 'wwwgjcom#getitem', param='北京',order='1234'))