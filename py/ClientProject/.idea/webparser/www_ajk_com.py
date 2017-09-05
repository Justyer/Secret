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
#             '楼盘物业类型','楼盘绿化率','楼盘物业费','数据来源','城市','行政区','str_order')                    #41

metadatas = ('信息来源','城市','行政区','片区','来源链接','题名','小区名称','小区链接','地址','建成年份','房龄',                     #10
             '楼层','总楼层','当前层','朝向','建筑面积','使用面积','户型','卧室数量','客厅数量','卫生间数量',                        #20
             '厨房数量','阳台数量','总价','单价','本月均价','小区开盘单价','住宅类别','产权性质','装修情况','建筑类别',               #30
             '楼盘物业类型','小区简介','联系人','联系人链接','经纪公司','门店','电话号码','服务商圈','注册时间','经纪公司房源编号',    #40
             '发布时间','小区总户数','小区总建筑面积','容积率','小区总停车位','开发商','交通状况','配套设施','楼盘绿化率','物业公司',  #50
             '楼盘物业费','土地使用年限','入住率','学校','地上层数','花园面积','地下室面积','车库数量','车位数量','厅结构',           #60
             '导航','房屋图片','纬度','经度','str_order','数据来源')                                                                                       #65

import requests, re, datetime
from bs4 import BeautifulSoup, Tag
#from requests.exceptions import RequestException
class myException(Exception):pass
#解析安居客网站
class wwwajkcom(ParserBase):
    headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36 LBBROWSER', 'Connection': 'keep-alive'}
    htmlwrite = HtmlFile()
    shi = re.compile(r'(\d+)室|卧|卧室')
    ting = re.compile(r'(\d+)厅')
    wei = re.compile(r'(\d+)卫')
    chu = re.compile(r'(\d+)厨')
    yangtai = re.compile(r'(\d+)(台|阳台)')

    def __init__(self):
        super(wwwajkcom, self).__init__()

    def default(self, urlbase):
        LOG.info('安居客默认方法获得城市列表!')
        time.sleep(1)
        r = requests.get(urlbase.url,headers=self.headers, timeout=(3.05, 3.5))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwajkcom %s 返回状态:%s', urlbase.url, r.status_code)
            return None
        soup = BeautifulSoup(r.content.decode('utf8'), 'html.parser') #lxml
        str_title = soup.find('title').text
        if str_title == '访问验证-安居客':
            time.sleep(5)
            raise myException('访问验证-安居客')
        citys = soup.find('div', class_='left_side').find_all('a')
        citys.extend(soup.find('div', class_='right_side').find_all('a'))

        list = []
        i_count = 1
        i_order = urlbase.order+'0'
        t_91 = ('上海',)
        t_45 = ('北京','深圳')
        t_25 = ('厦门','杭州','长沙','济南')
        t_17 = ('广州','苏州','成都')
        t_14 = ('天津',)
        t_12 = ('南京','合肥','武汉','石家庄')
        t_8 = ('重庆','温州','昆山','青岛','昆明','东莞','郑州','大连','福州')
        t_2 = ('日照','衢州','毕节','泸州','铜陵','滁州','荆门','德阳','大丰',
               '锦州','绥化','章丘','张掖','延安','泰州','开封','郴州','本溪',
               '运城','承德','济源','池州','荆州','辽阳','赣州','湘西','桐城',
               '邵阳','漳州','清远','宿迁','南充','咸宁','惠州','丽水','河源',
               '济宁','赤峰','庆阳','朔州','潮州','新余','丹东','晋城','巴中',
               '禹州','淮北','常州','拉萨','银川','梧州','通辽','咸阳','威海',
               '遵义','安康','黄山','株洲','鸡西','汉中','达州','定州','湘潭',
               '长治','贺州','蚌埠','宜春','焦作','柳州','绵阳','临汾','嘉兴',
               '义乌','随州','红河','安庆','洛阳','玉林','抚顺','凉山','大理',
               '濮阳','阳春','伊犁','孝感','芜湖','遂宁','宁波','亳州','武威',
               '金昌','沧州','昌吉','延边','永州','临沂','漯河','钦州','沭阳',
               '菏泽','常德','舟山','湛江','盐城','湖州','天水','枣庄','台山',
               '松原','哈密','攀枝花','广元','鹰潭','宣城','安顺','中山','益阳',
               '辽源','吴忠','贵阳','宝鸡','十堰','长葛','忻州','三亚','鄢陵','白山','百色')
        #定义一个系数
        ra = 1.0
        hour = datetime.datetime.now().strftime("%H")
        if hour in ('23', '00', '01', '02', '03', '04', '05'):
            ra = 0.5
        elif hour in ('20', '21', '22', '06', '07'):
            ra = 0.8
        for i in citys:
            #if i.text not in ('北京', '上海', '广州', '深圳'): continue
            #如果是苏州需要特殊处理URL链接
            if i.text== '苏州':
                i['href']="http://suzhou.anjuke.com"
            elif i.text=='无锡':
                i['href']="http://wuxi.anjuke.com"
            if i.text in t_91:
                i_count = 1
                while i_count <= 91*ra:
                    list.append(UrlBean(i['href']+'/sale/o5-p'+str(i_count)+'/', self.message('getpages'), param=i_count, headers=i.text, order=i_order))
                    LOG.info('获得城市%s页面信息%s', i.text, i['href']+'/sale/o5-p'+str(i_count)+'/')
                    i_count += 1
            elif i.text in t_45:
                i_count = 1
                while i_count <= 45*ra:
                    list.append(UrlBean(i['href']+'/sale/o5-p'+str(i_count)+'/', self.message('getpages'), param=i_count, headers=i.text, order=i_order))
                    LOG.info('获得城市%s页面信息%s', i.text, i['href']+'/sale/o5-p'+str(i_count)+'/')
                    i_count += 1
            elif i.text in t_25:
                i_count = 1
                while i_count <= 25*ra:
                    list.append(UrlBean(i['href']+'/sale/o5-p'+str(i_count)+'/', self.message('getpages'), param=i_count, headers=i.text, order=i_order))
                    LOG.info('获得城市%s页面信息%s', i.text, i['href']+'/sale/o5-p'+str(i_count)+'/')
                    i_count += 1
            elif i.text in t_17:
                i_count = 1
                while i_count <= 17*ra:
                    list.append(UrlBean(i['href']+'/sale/o5-p'+str(i_count)+'/', self.message('getpages'), param=i_count, headers=i.text, order=i_order))
                    LOG.info('获得城市%s页面信息%s', i.text, i['href']+'/sale/o5-p'+str(i_count)+'/')
                    i_count += 1
            elif i.text in t_14:
                i_count = 1
                while i_count <= 14*ra:
                    list.append(UrlBean(i['href']+'/sale/o5-p'+str(i_count)+'/', self.message('getpages'), param=i_count, headers=i.text, order=i_order))
                    LOG.info('获得城市%s页面信息%s', i.text, i['href']+'/sale/o5-p'+str(i_count)+'/')
                    i_count += 1
            elif i.text in t_12:
                i_count = 1
                while i_count <= 12*ra:
                    list.append(UrlBean(i['href']+'/sale/o5-p'+str(i_count)+'/', self.message('getpages'), param=i_count, headers=i.text, order=i_order))
                    LOG.info('获得城市%s页面信息%s', i.text, i['href']+'/sale/o5-p'+str(i_count)+'/')
                    i_count += 1
            elif i.text in t_8:
                i_count = 1
                while i_count <= 8*ra:
                    list.append(UrlBean(i['href']+'/sale/o5-p'+str(i_count)+'/', self.message('getpages'), param=i_count, headers=i.text, order=i_order))
                    LOG.info('获得城市%s页面信息%s', i.text, i['href']+'/sale/o5-p'+str(i_count)+'/')
                    i_count += 1
            elif i.text in t_2:
                i_count = 1
                while i_count <= 2*ra:
                    list.append(UrlBean(i['href']+'/sale/o5-p'+str(i_count)+'/', self.message('getpages'), param=i_count, headers=i.text, order=i_order))
                    LOG.info('获得城市%s页面信息%s', i.text, i['href']+'/sale/o5-p'+str(i_count)+'/')
                    i_count += 1
            else:
                # 更改为采集4页
                i_count = 1
                while i_count <= 4*ra:
                    list.append(UrlBean(i['href']+'/sale/o5-p'+str(i_count)+'/', self.message('getpages'), param=i_count, headers=i.text, order=i_order))
                    LOG.info('获得城市%s页面信息%s', i.text, i['href']+'/sale/o5-p'+str(i_count)+'/')
                    i_count += 1
        return list

    #解析城市二手房列表页
    def getpages(self, urlbase):
        LOG.info('ajkgetpages获得城市%s二手房列表信息', urlbase.url)
        time.sleep(2.5)
        r = requests.get(urlbase.url,headers=self.headers, timeout=(3.05, 3.5))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwajkcom %s 返回状态:%s', urlbase.url, r.status_code)
            return None
        html = r.content.decode('utf8',errors='ignore')
        soupall =  BeautifulSoup(html, 'html.parser') #lxml
        str_title = soupall.find('title').text
        if str_title == '访问验证-安居客':
            time.sleep(5)
            raise myException('访问验证-安居客')
        if soupall.find('ul', id='house-list'):
            htmllist = '<ul id="house-list" class="house-list">'+html.split('<ul id="house-list" class="house-list">')[1].split('<div id="IFX_p937" class="" style=""></div>')[0]
        elif soupall.find('ul', id='houselist-mod'):
            htmllist = '<ul id="houselist-mod" class="houselist-mod">'+html.split('<ul id="houselist-mod" class="houselist-mod">')[1].split('<div id="IFX_p937" class="" style=""></div>')[0]
        else:
            raise myException('安居客解析列表页面出错!')
        soup = BeautifulSoup(htmllist, 'html.parser')
        items = soup.find_all('a')
        list = []
        itemIndex = 1
        i_order = urlbase.order+'1'
        for item in items:
            if 'prop/view' in item['href']: #and '.58.com' not in item['href'] and 'fang_shou' not in item['href'] and 'fang_zu' not in item['href']:
                sUrl = item['href'].split('?')[0]
                list.append(UrlBean(sUrl, self.message('getitem'), key=sUrl, param=urlbase.headers, order=i_order))
                LOG.debug('%s第%d页%d项' % (urlbase.headers, urlbase.param, itemIndex))
                itemIndex += 1
        #存在分页信息
        # if urlbase.param and urlbase.param<=self.fetchpage:
        #     #获得下一页地址
        #     nextpage = soup.find('div', id='house-area')
        #     if nextpage:
        #         nextpageurl = nextpage.find('a', class_='next')
        #         if nextpageurl:
        #             host = '/'.join(r.url.split('/')[:3])
        #             list.append(UrlBean(host+nextpageurl['href'], self.message('getpages'), param=urlbase.param+1, headers=urlbase.headers))
        #             LOG.debug('%s第%d页' % (urlbase.headers, urlbase.param))
        return list;

    #解析详细页面信息
    #@retries(10, delay=1, backoff=1, exceptions=(RequestException))
    def getitem(self, urlbase):
        LOG.info('ajkgetinfo获得城市%s挂牌详细信息', urlbase.url)
        time.sleep(2.5)
        t1 = time.time()
        r = requests.get(urlbase.url,headers=self.headers, timeout=(3.05, 3.5))
        t2 = time.time()
        LOG.info('处理ajk请求getitem耗时:%f' % (t2-t1))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        #存储页面信息
        t1 = time.time()
        self.htmlwrite.save('%s\\%s\\%s' %(self.__class__.__name__, '二手房', urlbase.param), r.url, r.text)
        t2 = time.time()
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwajkom %s 返回状态:%s', r.request.url, r.status_code)
            return
        t1 = time.time()
        reText = r.text
        soup = BeautifulSoup(r.content.decode('utf8'), 'html.parser') #lxml
        lr = {}
        ###############################################################################################################
        str_title = soup.find('title').text
        if str_title == '访问验证-安居客':
            time.sleep(5)
            raise myException('访问验证-安居客')

        def _split(str_all, str, index):
            try:
                return _strip(str_all).split(str)[index]
            except Exception:
                return ''

        def _strip(str_info):
            return str_info.strip().replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '')

        lr[metadatas[4]] = urlbase.url
        #增加一个模板分支,杭州实勘房源模板解析
        if (''.join(r.url.split('/')[-1:]).upper().startswith('G')):
            try:
                lr[metadatas[5]] = soup.find('span', class_='title-content').getText(strip=True)
            except Exception as e:
                lr[metadatas[5]] =''

            try:
                lr[metadatas[6]] = soup.find('span', class_='report_tip', text=re.compile('小区：?')).parent.find('a').text
            except:
                lr[metadatas[6]] =''

            try:
                lr[metadatas[7]] = soup.find('span', class_='report_tip', text=re.compile('小区：?')).parent.find('a')['href']
            except:
                lr[metadatas[7]] = ''

            try:
                lr[metadatas[61]] = soup.find('div', class_='crumbs_wrap').getText(strip=True)
            except:
                lr[metadatas[61]] = ''

            try:
                lr[metadatas[8]] = soup.find('span', class_='report_tip', text=re.compile('地址：?')).parent.find('span', id='addrBlock').getText(strip=True)
            except:
                lr[metadatas[8]] = ''

            try:
                nfstr = soup.find('span', class_='report_tip', text=re.compile('小区：?')).parent.getText(strip=True)
                lr[metadatas[9]] = re.search('([\d]*)年建?', nfstr).group(1)
            except:
                lr[metadatas[9]] =''

            try:
                lcstr = soup.find('span', class_='report_tip', text=re.compile('楼层：?')).parent.getText(strip=True)
                lr[metadatas[11]] = re.sub('楼层[:：]?', '', lcstr)
            except:
                lr[metadatas[11]] =''

            try:
                lr[metadatas[12]] = re.search('[(（]共?(\d*)层?[)）]', lcstr, re.S).group(1)
            except:
                lr[metadatas[12]] = ''

            try:
                lr[metadatas[13]] = re.search('[:：]\s*(\d*)', lcstr, re.S).group(1)
            except:
                lr[metadatas[13]] = ''

            try:
                cxstr = soup.find('span', class_='report_tip', text=re.compile('朝向：?')).parent.getText(strip=True)
                lr[metadatas[14]] = re.sub('朝向：?', '', cxstr)
            except:
                lr[metadatas[14]] =''

            try:
                mjstr = soup.find('span', class_='report_tip', text=re.compile('面积：?')).parent.getText(strip=True)
                lr[metadatas[15]] = re.search('面积：(\d+\.?\d*)m²', mjstr).group(1)
            except:
                lr[metadatas[15]] =''

            try:
                lr[metadatas[29]] = soup.find('span', class_='report_tip', text=re.compile('装修：?')).parent.getText(strip=True).split('：')[1]
            except:
                lr[metadatas[29]] =''

            try:
                lr[metadatas[17]] = soup.find('span', class_='report_tip', text=re.compile('户型：?')).parent.getText(strip=True).split('：')[1]
            except:
                lr[metadatas[17]] =''
            try:
                lr[metadatas[18]] = re.search(wwwajkcom.shi,lr[metadatas[17]]).group(1)
            except:
                lr[metadatas[18]] = ''
            try:
                lr[metadatas[19]] = re.search(wwwajkcom.ting,lr[metadatas[17]]).group(1)
            except:
                lr[metadatas[19]] = ''
            try:
                lr[metadatas[20]] = re.search(wwwajkcom.wei,lr[metadatas[17]]).group(1)
            except:
                lr[metadatas[20]] = ''
            try:
                lr[metadatas[21]] = re.search(wwwajkcom.chu,lr[metadatas[17]]).group(1)
            except:
                lr[metadatas[21]] = ''
            try:
                lr[metadatas[22]] = re.search(wwwajkcom.yangtai,lr[metadatas[17]]).group(1)
            except:
                lr[metadatas[22]] = ''

            try:
                lr[metadatas[24]] = re.search('(\d+)元', soup.find('span', class_='unit_price').getText(strip=True)).group(1)
            except:
                lr[metadatas[24]] =''

            try:
                lr[metadatas[23]] = soup.find('span', class_='entrust_price').find('em', class_='price_num').getText(strip=True)
            except:
                lr[metadatas[23]] = ''

            try:
                lr[metadatas[33]] = soup.find('div', class_='a-broker').find('p', class_='broker-name').getText(strip=True)
            except:
                lr[metadatas[33]] = ''

            try:
                lr[metadatas[34]] = soup.find('div', class_='a-broker').find('a', class_='broker-info')['href']
            except:
                lr[metadatas[34]] = ''

            try:
                lr[metadatas[35]] = ''
            except:
                lr[metadatas[35]] = ''

            try:
                lr[metadatas[36]] = ''
            except:
                lr[metadatas[36]] = ''

            try:
                lr[metadatas[37]] = soup.find('div', class_='a-broker').find('p', class_='broker-num').getText(strip=True)
            except:
                lr[metadatas[37]] = ''

            try:
                lr[metadatas[63]] = ''
            except:
                lr[metadatas[63]] = ''

            try:
                lr[metadatas[64]] = ''
            except:
                lr[metadatas[64]] = ''

            try:
                lr[metadatas[40]] = str(soup.find('span', class_='report_sub_title', text=re.compile('房屋编码：?')).next_sibling).strip()
            except:
                lr[metadatas[40]] = ''

            try:
                fb_time = str(soup.find('span', class_='report_sub_title', text=re.compile('实勘时间：?')).next_sibling).strip()
                lr[metadatas[41]] = fb_time.replace('年','-').replace('月','-').replace('日','')
            except:
                lr[metadatas[41]] = ''

            try:
                #zhs = re.findall('总户数</dt>(.*?)</dd>',reText,re.S)[0]
                lr[metadatas[42]] = ''
            except:
                lr[metadatas[42]] = ''

            try:
                #zjmj = re.findall('总建面积</dt>(.*?)</dd>',reText,re.S)[0]
                lr[metadatas[43]] = ''
            except:
                lr[metadatas[43]] = ''

            try:
                #rjl = re.findall('容积率</dt>(.*?)</dd>',reText,re.S)[0]
                lr[metadatas[44]] = ''
            except:
                lr[metadatas[44]] = ''

            try:
                #tcw = re.findall('停车位</dt>(.*?)</dd>',reText,re.S)[0]
                lr[metadatas[45]] = soup.find('span', class_='report_tip', text=re.compile('车位：?')).parent.getText(strip=True).split('：')[1]
            except:
                lr[metadatas[45]] = ''

            try:
                #kfs = re.findall('开发商</dt>(.*?)</dd>',reText,re.S)[0]
                lr[metadatas[46]] = ''
            except:
                lr[metadatas[46]] = ''

            try:
                lr[metadatas[47]] = soup.find('span', class_='report_tip', text=re.compile('交通：?')).parent.getText(strip=True).split('：')[1]
            except:
                lr[metadatas[47]] = ''

            try:
                lr[metadatas[54]] = soup.find('span', class_='report_tip', text=re.compile('教育：?')).parent.getText(strip=True).split('：')[1]
            except:
                lr[metadatas[54]] = ''

            try:
                lr[metadatas[50]] = ''
            except:
                lr[metadatas[50]] = ''

            try:
                lr[metadatas[27]] = soup.find('span', class_='report_tip', text=re.compile('类型：?')).parent.getText(strip=True).split('：')[1]
            except:
                 lr[metadatas[27]] = ''

            try:
                lr[metadatas[31]] = lr[metadatas[27]]
            except:
                lr[metadatas[31]] = ''

            try:
                lr[metadatas[49]] = ''
            except:
                lr[metadatas[49]] =''

            try:
                lr[metadatas[51]] = ''
            except:
                lr[metadatas[51]] = ''

            try:
                lr[metadatas[1]] = lr[metadatas[61]].split('>')[0].replace('房产网', '')
            except:
                lr[metadatas[1]] = ''

            try:
                lr[metadatas[2]] = lr[metadatas[61]].split('>')[2].replace('二手房', '')
            except:
                lr[metadatas[2]] = ''

            try:
                #lr[metadatas[3]] = soup.find('span', class_='report_tip', text=re.compile('地址：?')).parent.find('a', text=re.compile('-(.)*-')).getText(strip=True).replace('-', '')
                if lr[metadatas[61]].split('>')[3].endswith('二手房'):
                    lr[metadatas[3]] = lr[metadatas[61]].split('>')[3].replace('二手房', '')
                else:
                    lr[metadatas[3]] = ''
            except:
                lr[metadatas[3]] = ''

            try:
                lr[metadatas[48]] = soup.find('dt', class_='report_sub_titles', text=re.compile('配套设施')).next_sibling.next_sibling.getText(strip=True)
            except:
                lr[metadatas[48]] = ''

        else:
            try:
                title = re.findall('<h3 class="fl">(.*?)</h3>',reText,re.S) \
                        or re.findall('<h3 class="long-title">(.*?)</h3>',reText,re.S)
                lr[metadatas[5]]  = title[0]
            except Exception as e:
                lr[metadatas[5]]  =''

            try:
                xq = re.findall('<dt>所?在?小区：?</dt>(.*?)</dd>',reText,re.S)
                dr = re.compile(r'<[^>]+>',re.S)
                lr[metadatas[6]] = dr.sub('',xq[0]).replace('（租套，售套）','').replace('（租套 售套）', '').replace('暂无','').strip()
            except:
                lr[metadatas[6]] =''

            try:
                lr[metadatas[3]] =''
                area1 = soup.find('div',attrs={'class':'block-area'}).find_all('a')
                for area2 in area1:
                     lr[metadatas[3]] = area2.text.replace('房价','')
            except:
                lr[metadatas[3]] =''

            try:
                xq = re.findall('小区名?：?</dt>(.*?)target="_blank">',reText,re.S)
                xq_link = re.findall('<a href="(.*?)"',str(xq),re.S)
                lr[metadatas[7]] = xq_link[0]
            except:
                lr[metadatas[7]] =''

            try:
                ld_name = re.findall('<div id="content">(.*?)</div>',reText,re.S)
                dr = re.compile(r'<[^>]+>',re.S)
                lr[metadatas[61]] = dr.sub('',ld_name[0]).replace('&gt;','>').replace('二手房','').strip()
            except:
                lr[metadatas[61]] =''

            try:
                address = re.findall('地址</dt>(.*?)<a href',reText,re.S) \
                          or soup.find('p', class_='loc-text').getText(strip=True).split('－')[-1:]
                dr = re.compile(r'<[^>]+>',re.S)
                lr[metadatas[8]] = dr.sub('',address[0]).strip().replace('\n', '')
            except:
                lr[metadatas[8]] = ''

            try:
                year = re.findall('建造年代</dt>(.*?)</dd>',reText,re.S) \
                       or [soup.find('dt', text=re.compile(r'年代：?')).find_next('dd').getText(strip=True).replace('年', '')]
                dr = re.compile(r'<[^>]+>',re.S)
                lr[metadatas[9]] = dr.sub('',year[0]).strip()
            except:
                lr[metadatas[9]] =''

            try:
                #z_floor = re.findall('楼层：?</dt>(.*?)</dl>',reText,re.S)[0]
                #dr = re.compile(r'<[^>]+>',re.S)
                #lr[metadatas[11]] = dr.sub('',z_floor).strip()
                z_floor = soup.find('dt', text=re.compile(r'楼层：?')).find_next('dd').getText(strip=True)
                lr[metadatas[11]] = z_floor
            except:
                lr[metadatas[11]] =''

            try:
                floor = re.findall('/(.*?)<',z_floor,re.S) \
                        or re.findall('共(\d*)层',z_floor,re.S)
                lr[metadatas[12]] = floor[0]
            except:
                lr[metadatas[12]] =''

            try:
                dq_floor = re.findall(r'([^层(（]+)',z_floor,re.S)
                lr[metadatas[13]] = '' if '共' in dq_floor[0] else dq_floor[0].replace('<','')
            except:
                lr[metadatas[13]] =''

            try:
                toward_t = re.findall('朝向：?</dt>(.*?)</dl>',reText,re.S)
                toward = re.findall('<dd>(.*?)</dd>',str(toward_t),re.S)
                lr[metadatas[14]] = toward[0]
            except:
                lr[metadatas[14]] =''

            try:
                jz_area = re.findall('面积：?</dt>(.*?)</dl>',reText,re.S)
                area = re.findall('<dd>(.*?)平方?米',str(jz_area),re.S)
                lr[metadatas[15]] = area[0]
            except:
                lr[metadatas[15]] =''

            try:
                decorate_t = re.findall('装修程?度?：?</dt>(.*?)</dl>',reText,re.S)
                decorate = re.findall('<dd>(.*?)</dd>',str(decorate_t),re.S)
                lr[metadatas[29]] = decorate[0]
            except:
                lr[metadatas[29]] =''

            try:
                huose_t = re.findall('房型：?</dt>(.*?)</dl>',reText,re.S)
                huose = re.findall('<dd>(.*?)</dd>',str(huose_t),re.S)
                huose = re.sub(r'[\\rnt\s]+', '', huose[0])
                lr[metadatas[17]] = huose
            except:
                lr[metadatas[17]] =''
            try:
                lr[metadatas[18]] = re.search(wwwajkcom.shi,lr[metadatas[17]]).group(1)
            except:
                lr[metadatas[18]] = ''
            try:
                lr[metadatas[19]] = re.search(wwwajkcom.ting,lr[metadatas[17]]).group(1)
            except:
                lr[metadatas[19]] = ''
            try:
                lr[metadatas[20]] = re.search(wwwajkcom.wei,lr[metadatas[17]]).group(1)
            except:
                lr[metadatas[20]] = ''
            try:
                lr[metadatas[21]] = re.search(wwwajkcom.chu,lr[metadatas[17]]).group(1)
            except:
                lr[metadatas[21]] = ''
            try:
                lr[metadatas[22]] = re.search(wwwajkcom.yangtai,lr[metadatas[17]]).group(1)
            except:
                lr[metadatas[22]] = ''

            try:
                u_price_t = re.findall('房?屋?单价：?</dt>(.*?)</dl>',reText,re.S)
                u_price = re.findall('<dd>(.*?)元',str(u_price_t),re.S)
                lr[metadatas[24]] = u_price[0]
            except:
                lr[metadatas[24]] =''

            try:
                t_price_t = re.findall('售价</dt>(.*?)</dl>',reText,re.S)
                t_price = re.findall('<strong><span class="f26">(.*?)<',str(t_price_t),re.S) \
                        or [soup.find('span', class_='light info-tag').em.getText(strip=True)]
                lr[metadatas[23]] = t_price[0]
            except:
                lr[metadatas[23]] =''

            try:
                lxr_name = re.findall('<strong class="name">(.*?)<',reText,re.S) \
                           or [soup.find('p', class_='broker-name').getText(strip=True)]
                lr[metadatas[33]] = lxr_name[0]
            except:
                lr[metadatas[33]] =''

            try:
                lr[metadatas[34]] = (soup.find('div',class_='broker_more_box') or soup.find('p', class_='broker-name')).find('a')['href']
            except:
                lr[metadatas[34]] = ''

            try:
                # company = re.findall('<p class="comp_info">(.*?)</a>',reText,re.S)
                # dr = re.compile(r'<[^>]+>',re.S)
                # lr[metadatas[35]] = dr.sub('',company[0]).strip()
                company = (soup.find('p', class_='comp_info') \
                           or soup.find('div', class_='broker-company')).find('a')
                if hasattr(company.attrs, 'title'):
                    lr[metadatas[35]] = company.getattr('title')
                else:
                    lr[metadatas[35]] = company.getText(strip=True).replace('...', '')
            except:
                lr[metadatas[35]] =''

            try:
                lr[metadatas[36]] = soup.find('div',class_='broker_name').find_all('a')[1]['title']
            except:
                lr[metadatas[36]] = ''

            try:
                if lr[metadatas[36]] == '':
                    lr[metadatas[36]] = soup.find('div', class_='broker-company').find_all('a')[1].getText(strip=True).replace('...', '')
            except:pass

            try:
                telephone = re.findall('<div class="broker_icon broker_tel dark_grey"><i class="p_icon icon_tel"></i>(.*?)</div>',reText,re.S) \
                            or re.findall('<i class="ico tele_ico"></i>([^<]*)',reText,re.S) \
                            or [re.sub(r'\s+', '', soup.find('p', class_='broker-mobile').getText(strip=True))]
                dr = re.compile(r'<[^>]+>',re.S)
                lr[metadatas[37]] = dr.sub('',telephone[0]).strip()
            except:
                lr[metadatas[37]] =''

            try:
                lng = re.findall('\'comm_lng\' : \'(.*?)\'',reText,re.S)
                lr[metadatas[64]] = lng[0]
            except:
                lr[metadatas[64]] =''

            try:
                lat = re.findall('\'comm_lat\' : \'(.*?)\'',reText,re.S)
                lr[metadatas[63]] = lat[0]
            except:
                lr[metadatas[63]] =''

            try:
                fybh= re.findall('<div class="text-mute extra-info">房源编号：(.*?)，',reText,re.S) \
                      or re.search(r'(\d+)', soup.find('h4', class_='houseInfo-title').getText(strip=True)).groups()
                lr[metadatas[40]] = fybh[0]
            except:
                lr[metadatas[40]] =''

            try:
                fb_time = (soup.find('div',class_='text-mute extra-info') \
                           or soup.find('h4', class_='houseInfo-title')).text
                lr[metadatas[41]] = _split(fb_time,'，发布时间：',1).replace('年','-').replace('月','-').replace('日','')
            except:
                lr[metadatas[41]] =''

            try:
                zhs = re.findall('总户数：?</dt>(.*?)</dd>',reText,re.S)[0]
                lr[metadatas[42]] = _strip(zhs.replace('<dd>',''))
            except:
                lr[metadatas[42]] = ''

            try:
                zjmj = (re.findall('总建面积</dt>(.*?)</dd>',reText,re.S) \
                        or re.findall('总建面：?</dt>(.*?)</dd>',reText,re.S))[0]
                lr[metadatas[43]] = _split(zjmj.replace('<dd>',''),'平方米',0)
            except:
                lr[metadatas[43]] = ''

            try:
                rjl = re.findall('容积率：?</dt>(.*?)</dd>',reText,re.S)[0]
                lr[metadatas[44]] = _strip(rjl.replace('<dd>',''))
            except:
                lr[metadatas[44]] = ''

            try:
                tcw = re.findall('停车位：?</dt>(.*?)</dd>',reText,re.S)[0]
                lr[metadatas[45]] = _strip(tcw.replace('<dd>',''))
            except:
                lr[metadatas[45]] = ''

            try:
                kfs = re.findall('开发商：?</dt>(.*?)</dd>',reText,re.S)[0]
                lr[metadatas[46]] = _strip(kfs.replace('<dd>',''))
            except:
                lr[metadatas[46]] = ''

            try:
                jtzk = re.findall('交通优势：</span></strong></p>(.*?)</span></p>',reText,re.S)[0]
                dr = re.compile(r'<[^>]+>',re.S)
                lr[metadatas[47]] = dr.sub('',jtzk).strip()
            except:
                lr[metadatas[47]] = ''


            try:
                xx = re.findall('学校：(.*?)</span></p>',reText,re.S)[0]
                dr = re.compile(r'<[^>]+>',re.S)
                lr[metadatas[54]] = dr.sub('',xx).strip()[0:200]
            except:
                lr[metadatas[54]] = ''

            try:
                wygs = re.findall('物业公司：?</dt>(.*?)</dd>',reText,re.S)[0]
                lr[metadatas[50]] = _strip(wygs.replace('<dd>',''))
            except:
                lr[metadatas[50]] = ''

            try:
                zz_category = re.findall('类型：?</dt>(.*?)</dl>',reText,re.S)
                category1 = re.findall('<dd>(.*?)</dd>',str(zz_category),re.S)
                category = category1[1]
                lr[metadatas[27]] = category.replace("\n","").strip()
            except:
                 lr[metadatas[27]] =''


            try:
                lpwylx_t = re.findall('物业类型：?</dt>(.*?)</dl>',reText,re.S)
                lpwylx = re.findall('<dd>(.*?)</dd>',str(lpwylx_t),re.S)
                lr[metadatas[31]] = lpwylx[0]
            except:
                lr[metadatas[31]] =''

            try:
                greening = re.findall('绿化率：?</dt>(.*?)</dl>',reText,re.S)
                green = re.findall('<dd>(.*?)</dd>',str(greening),re.S)
                lr[metadatas[49]] = green[0]
            except:
                lr[metadatas[49]] =''

            try:
                costs_t = re.findall('物业费用：?</dt>(.*?)</dl>',reText,re.S)
                costs = re.findall('<dd>(.*?)</dd>',str(costs_t),re.S)
                lr[metadatas[51]] = costs[0]
            except:
                lr[metadatas[51]] =''



            try:
                city = re.findall('<span class="city">(.*?)<',reText,re.S)
                lr[metadatas[1]] =city[0]
            except:
                lr[metadatas[1]] =''


            try:
                xz_area1 = re.findall('位置：?</dt>(.*?)/a>',reText,re.S)
                xz_area = re.findall(r'">([^<]+?)<',str(xz_area1),re.S)
                lr[metadatas[2]] = xz_area[0]
            except:
                lr[metadatas[2]] =''

            lr[metadatas[48]] = ''

        lr[metadatas[0]] = 's00000aj'
        lr[metadatas[65]] = urlbase.order if urlbase.order is not None else ''
        lr[metadatas[66]] = 'ajk'

        lr[metadatas[10]] = ''
        lr[metadatas[16]] = ''
        lr[metadatas[25]] = ''
        lr[metadatas[26]] = ''
        lr[metadatas[28]] = ''
        lr[metadatas[30]] = ''
        lr[metadatas[32]] = ''
        lr[metadatas[38]] = ''
        lr[metadatas[39]] = ''

        lr[metadatas[52]] = ''
        lr[metadatas[53]] = ''
        lr[metadatas[55]] = ''
        lr[metadatas[56]] = ''
        lr[metadatas[57]] = ''
        lr[metadatas[58]] = ''
        lr[metadatas[59]] = ''
        lr[metadatas[60]] = ''
        lr[metadatas[62]] = ''
        ###############################################################################################################
        t2 = time.time()
        LOG.info('解析页面耗时:%f' % (t2-t1))
        # print(metadatas[1], lr[metadatas[1]], '|',
        #       metadatas[2], lr[metadatas[2]], '|',
        #       metadatas[3], lr[metadatas[3]], '|',
        #       metadatas[6], lr[metadatas[6]], '|',
        #       metadatas[15], lr[metadatas[15]], '|',
        #       metadatas[23], lr[metadatas[23]], '|',
        #       metadatas[24], lr[metadatas[24]], '|',
        #       metadatas[37], lr[metadatas[37]])
        #将分析的信息写入数据库
        #www58com.mysql.save(lr, metadatas)
        if lr[metadatas[1]].strip() == '':
            raise myException('数据错误,城市字段为空!')
        self.completionlr(lr, metadatas)
        MySqlEx.save(lr, metadatas)

    #def getinfo(self, urlbase):
        #LOG.info('58getinfo获得%s挂牌详细信息' , urlbase.url)


if __name__ == '__main__':
    wajk = wwwajkcom()
    #print(len(wajk.default(UrlBase('http://www.anjuke.com/sy-city.html', 'wwwajkcom',order='123'))))
    #print(len(wajk.getpages(UrlBean('http://shanghai.anjuke.com/sale/o5-p2/', 'wwwajkcom#getitem', param=10, headers='哈尔滨',order='123'))))
    #print(len(wajk.getpages(UrlBean('http://hangzhou.anjuke.com/sale/p2/', 'wwwajkcom#getitem', param=10, headers='哈尔滨',order='123'))))
    #wajk.getitem(UrlBean('http://guangzhou.anjuke.com/prop/view/A505200901', 'wwwajkcom#getitem', param=9, headers='哈尔滨',order='123456'))
    #wajk.getitem(UrlBean('http://hangzhou.anjuke.com/prop/view/G41530', 'wwwajkcom#getitem', param=9, headers='哈尔滨',order='123456'))
    wajk.getitem(UrlBean('http://beijing.anjuke.com/prop/view/A513039609', 'wwwajkcom#getitem', param=9, headers='哈尔滨',order='123456'))
    wajk.getitem(UrlBean('http://beijing.anjuke.com/prop/view/A512905005', 'wwwajkcom#getitem', param=9, headers='哈尔滨',order='123456'))
    wajk.getitem(UrlBean('http://hangzhou.anjuke.com/prop/view/A513019093', 'wwwajkcom#getitem', param=9, headers='哈尔滨',order='123456'))
