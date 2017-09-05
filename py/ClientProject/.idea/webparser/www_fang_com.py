# coding=gbk
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
LOG.handlers[1].setLevel(logging.DEBUG)

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
             '导航','房屋图片','纬度','经度','str_order','数据来源')                                                                                      #65

import socket,time
#socket.timeout = 3
import requests, re
from bs4 import BeautifulSoup, Tag
from requests.exceptions import RequestException
class myException(Exception):pass
#解析搜房网站
class wwwfangcom(ParserBase):
    htmlwrite = HtmlFile()
    headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36 LBBROWSER', 'Connection': 'keep-alive'}
    shi = re.compile(r'(\d+)室|卧|卧室')
    ting = re.compile(r'(\d+)厅')
    wei = re.compile(r'(\d+)卫')
    chu = re.compile(r'(\d+)厨')
    yangtai = re.compile(r'(\d+)台|阳台')

    pagenotfound = '房源不存在！'

    t_90 = ('北京','上海')
    t_45 = ('深圳','苏州','杭州')
    t_30 = ('天津',)
    t_25 = ('广州',)
    t_15 = ('重庆','成都','南京','青岛','厦门','郑州','珠海','武汉','济南','东莞')
    t_7  = ('保定','贵阳','长春','桂林','石家庄','合肥','长沙','昆明','宁波','烟台','沈阳','太原',
            '大连','西安','呼和浩特','哈尔滨','无锡','常州','佛山','福州','海南','惠州','江门',
            '江阴','昆山','廊坊','兰州','洛阳','南昌','南宁','南通','秦皇岛','泉州','三亚','泰州','唐山','潍坊','威海',
            '湘潭','咸阳','徐州','扬州','宜昌','银川','中山',
            '温州','金华','漳州','乌鲁木齐','嘉兴','九江','吉林','淮安','常德', '西宁', '鞍山', '石河子', '大庆', '防城港',
            '衡水','滨州','遂宁','黄石','昌吉','伊犁','阿克苏','庆阳')

    #提供给小地市脚本判断城市
    t_all = (t_90, t_45, t_30, t_25, t_15, t_7)
    @staticmethod
    def hasCity(str):
        for t in wwwfangcom.t_all:
            if str in t:
                return True
        return False

    def __init__(self):
        super(wwwfangcom, self).__init__()

    def default(self, urlbase):
        LOG.info('搜房默认方法获得城市列表!')
        r = requests.get(urlbase.url, headers=self.headers, timeout=(3.05, 3.5))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwfangcom %s 返回状态:%s', urlbase.url, r.status_code)
            return None
        soup = BeautifulSoup(r.content.decode('gbk', errors='ignore'), 'html.parser') #lxml
        citys = soup.find('div', id='c01').find_all('a')
        ls = []
        i_order = urlbase.order+'0'
        for i in citys:
            if i.text in self.t_90:
                i_count = 1
                while i_count <= 90:
                    ls.append(UrlBean(i['href']+'/house/h316-i3'+str(i_count)+'-j3100/', self.message('getpages'), param=i_count, headers=i.text, order=i_order))
                    LOG.info('获得城市%s页面信息%s', i.text, i['href']+'/house/h316-i3'+str(i_count)+'-j3100/')
                    i_count += 1
            elif i.text in self.t_45:
                i_count = 1
                while i_count <= 45:
                    ls.append(UrlBean(i['href']+'/house/h316-i3'+str(i_count)+'-j3100/', self.message('getpages'), param=i_count, headers=i.text, order=i_order))
                    LOG.info('获得城市%s页面信息%s', i.text, i['href']+'/house/h316-i3'+str(i_count)+'-j3100/')
                    i_count += 1
            elif i.text in self.t_30:
                i_count = 1
                while i_count <= 30:
                    ls.append(UrlBean(i['href']+'/house/h316-i3'+str(i_count)+'-j3100/', self.message('getpages'), param=i_count, headers=i.text, order=i_order))
                    LOG.info('获得城市%s页面信息%s', i.text, i['href']+'/house/h316-i3'+str(i_count)+'-j3100/')
                    i_count += 1
            elif i.text in self.t_25:
                i_count = 1
                while i_count <= 25:
                    ls.append(UrlBean(i['href']+'/house/h316-i3'+str(i_count)+'-j3100/', self.message('getpages'), param=i_count, headers=i.text, order=i_order))
                    LOG.info('获得城市%s页面信息%s', i.text, i['href']+'/house/h316-i3'+str(i_count)+'-j3100/')
                    i_count += 1
            elif i.text in self.t_15:
                i_count = 1
                while i_count <= 15:
                    ls.append(UrlBean(i['href']+'/house/h316-i3'+str(i_count)+'-j3100/', self.message('getpages'), param=i_count, headers=i.text, order=i_order))
                    LOG.info('获得城市%s页面信息%s', i.text, i['href']+'/house/h316-i3'+str(i_count)+'-j3100/')
                    i_count += 1
            elif i.text in self.t_7:
                i_count = 1
                while i_count <= 7:
                    ls.append(UrlBean(i['href']+'/house/h316-i3'+str(i_count)+'-j3100/', self.message('getpages'), param=i_count, headers=i.text, order=i_order))
                    LOG.info('获得城市%s页面信息%s', i.text, i['href']+'/house/h316-i3'+str(i_count)+'-j3100/')
                    i_count += 1
        return ls

    #解析城市二手房列表页
    def getpages(self, urlbase):
        LOG.info('fanggetpages获得城市%s二手房列表信息', urlbase.url)
        r = requests.get(urlbase.url, headers=self.headers, timeout=(3.05, 3.5))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwfangcom %s 返回状态:%s', urlbase.url, r.status_code)
            return None
        soup = BeautifulSoup(r.content.decode('gbk', errors='ignore'), 'html.parser') #lxml
        items = soup.find('div', attrs={'class':'houseList'}).find_all('a', attrs={'title': True})
        host = '/'.join(r.url.split('/')[:3])
        itemIndex = 1
        i_order = urlbase.order+'1'
        ls = []
        for item in items:
            if '/chushou/' in item['href']:
                strUrl = item['href'] if 'http' in item['href'].lower() else host+item['href']
                ls.append(UrlBean(strUrl, self.message('getitem'), key=strUrl, param=urlbase.headers, order=i_order))
                LOG.debug('%s第%d页%d项' % (urlbase.headers, urlbase.param, itemIndex))
                itemIndex += 1
        #存在分页信息
        # if urlbase.param and urlbase.param<=self.fetchpage:
        #     #获得下一页地址
        #     nextpage = soup.find('div', id='list_D10_15')
        #     if nextpage:
        #         nextpageurl = nextpage.find('a', id ='PageControl1_hlk_next')
        #         if nextpageurl:
        #             list.append(UrlBean(host+nextpageurl['href'], self.message('getpages'), param=urlbase.param+1, headers=urlbase.headers))
        #             LOG.debug('%s第%d页' % (urlbase.headers, urlbase.param))
        return ls

    #解析详细页面信息
    #@retries(10, delay=1, backoff=1, exceptions=(RequestException))
    def getitem(self, urlbase):
        LOG.info('fanggetinfo获得城市%s挂牌详细信息', urlbase.url)
        r = requests.get(urlbase.url, headers=self.headers, timeout=(3.05, 3.5))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        self.htmlwrite.save('%s\\%s\\%s' %(self.__class__.__name__, '二手房', urlbase.param), r.url, r.text)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwfangcom %s 返回状态:%s', urlbase.url, r.status_code)
            return
        soup = BeautifulSoup(r.content.decode('gbk', errors='ignore'), 'html.parser') #lxml
        #如果返回的是房源不存在页面就直接退出
        try:
            if self.pagenotfound in soup.getText(strip=True):
                LOG.info('url:%s %s', urlbase.url, self.pagenotfound)
                return
        except:pass
        reText = r.text
        lr = {}
        ###############################################
        def _split(str_all, str, index):
            try:
                return _strip(str_all).split(str)[index]
            except Exception:
                return ''

        def _strip(str_info):
            return str_info.strip().replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '')

        title_bs = soup.find('div',attrs={'class':'title'})
        try:
            lr[metadatas[5]] = _strip(title_bs.h1.string)
        except Exception:
            lr[metadatas[5]] = ''

        lr[metadatas[4]] = r.url

        time_zz = '([0-9]{3}[1-9]|[0-9]{2}[1-9][0-9]{1}|[0-9]{1}[1-9][0-9]{2}|[1-9][0-9]{3})-(((0[13578]|1[02])-(0[1-9]|[12][0-9]|3[01]))|((0[469]|11)-(0[1-9]|[12][0-9]|30))|(02-(0[1-9]|[1][0-9]|2[0-8])))'
        time_regexp = re.compile(time_zz)
        try:
            lr[metadatas[41]] = _strip(title_bs.find(text=time_regexp).string.replace('发布时间：', ''))
        except:
            lr[metadatas[41]] = ''

        city_Bs = soup.find('div', attrs={'class':'bread'})

        if city_Bs is not None:
            city = city_Bs.find_all('a')
            lr[metadatas[61]] = (">".join([_strip(dd.text) for dd in city])).replace('二手房', '').strip()
        try:
            lr[metadatas[1]] = _strip(city[1].string.replace('二手房', ''))
        except:
            lr[metadatas[1]] = ''
        try:
            lr[metadatas[2]] = _strip(city[2].string.replace('二手房', ''))
        except:
            lr[metadatas[2]] = ''

        agentInfo_bs = soup.find('div', attrs={'class':'agentInf'})
        if agentInfo_bs is not None:
            try:
                lr[metadatas[33]] = _strip(agentInfo_bs.find('span', attrs={'id': 'Span3'}).string)
            except Exception:
                lr[metadatas[33]] = ''
            try:
                lr[metadatas[34]] = agentInfo_bs.find('a')['href']
            except:
                lr[metadatas[34]] = ''
            if lr[metadatas[34]] != '':
                try:
                    rjjr = requests.get(lr[metadatas[34]], headers=self.headers, timeout=(3.05, 2.5))
                    reTextjjr = rjjr.text
                except:
                    reTextjjr = ''
                if '<div class="contentwrap">' not in reTextjjr:
                    try:
                        lr[metadatas[35]] = re.findall('公<span class="pl24">司</span>：(.*?)</li>',reTextjjr,re.S)[0]
                    except:
                        lr[metadatas[35]] = ''
                    try:
                        lr[metadatas[36]] = re.findall('<li>门店名称：(.*?)</li>',reTextjjr,re.S)[0]
                    except:
                        lr[metadatas[36]] = ''
                    try:
                        lr[metadatas[38]] = re.findall('服务商圈：(.*?)</li>',reTextjjr,re.S)[0]
                        if '</dd>' in lr[metadatas[38]]:
                            lr[metadatas[38]] = _split(lr[metadatas[38]],'</dd>',0)
                    except:
                        lr[metadatas[38]] = ''
                    try:
                        lr[metadatas[39]] = re.findall('<li>注册时间：(.*?)</li>',reTextjjr,re.S)[0]
                    except:
                        lr[metadatas[39]] = ''
                else:
                    try:
                        lr[metadatas[35]] = re.findall('</b><span class="">(.*?)</span>',reTextjjr,re.S)[0]
                    except:
                        lr[metadatas[35]] = ''
                    try:
                        md = re.findall('<li>所属门店：(.*?)</span>',reTextjjr,re.S)[0]
                        dr = re.compile(r'<[^>]+>',re.S)
                        lr[metadatas[36]] =  _strip(re.sub(dr,'',md))
                    except:
                        lr[metadatas[36]] = ''
                    try:
                        sq = re.findall('<li>服务商圈：(.*?)</span>',reTextjjr,re.S)[0]
                        dr = re.compile(r'<[^>]+>',re.S)
                        lr[metadatas[38]] =  _strip(re.sub(dr,'',sq))
                        if '</dd>' in lr[metadatas[38]]:
                            lr[metadatas[38]] = _split(lr[metadatas[38]],'</dd>',0)
                    except:
                        lr[metadatas[38]] = ''
                    try:
                        rzsj = re.findall('入职时间：(.*?)</li>',reTextjjr,re.S)[0]
                        dr = re.compile(r'<[^>]+>',re.S)
                        lr[metadatas[39]] =  _strip(re.sub(dr,'',rzsj))
                    except:
                        lr[metadatas[39]] = ''
        else:
            try:
                lr[metadatas[33]] = soup.find('div', class_='bookTel').find('a', class_='name').getText(strip=True).replace('业主', '')
            except:
                lr[metadatas[33]] = ''
            lr[metadatas[34]] = lr[metadatas[35]] = lr[metadatas[36]] = lr[metadatas[38]] = lr[metadatas[39]] = ''

        try:
            lr[metadatas[37]] = _strip((soup.find(id="mobilecode") \
                                        or soup.find("span", class_='tel')).getText(strip=True)
                                        or soup.find("input", id="AgentTel")['value'])
        except:
            lr[metadatas[37]] = ''
        try:
            lr[metadatas[40]] = re.findall('<span class="mr10">房源编号：(.*?)</span>',reText,re.S)[0]
        except:
            lr[metadatas[40]] = ''

        inforTxt_bs = soup.find('div', attrs={'class': 'inforTxt'})
        try:
            lr[metadatas[23]] = _strip(inforTxt_bs.find('span', {'class': 'red20b'}).string)
        except:
            lr[metadatas[23]] = ''
        try:
            lr[metadatas[24]] = _split(inforTxt_bs.dl.dt.text, '(', 1).split(')')[0].replace('元/㎡', '')
            if lr[metadatas[24]] == '':
                lr[metadatas[24]] = _split(inforTxt_bs.dl.dt.text, '（', 1).split('）')[0].replace('元/㎡', '')
        except:
            lr[metadatas[24]] = ''
        fit_str = "".join([dd.text for dd in inforTxt_bs.find('dl').find_all('dd')])
        # print('fit_str', fit_str)
        try:
            lr[metadatas[17]] = _split(fit_str, '户型：', 1).split('建筑面积：')[0]
        except:
            lr[metadatas[17]] = ''
        try:
            lr[metadatas[18]] = re.search(wwwfangcom.shi,lr[metadatas[17]]).group(1)
        except:
            lr[metadatas[18]] = ''
        try:
            lr[metadatas[19]] = re.search(wwwfangcom.ting,lr[metadatas[17]]).group(1)
        except:
            lr[metadatas[19]] = ''
        try:
            lr[metadatas[20]] = re.search(wwwfangcom.wei,lr[metadatas[17]]).group(1)
        except:
            lr[metadatas[20]] = ''
        try:
            lr[metadatas[21]] = re.search(wwwfangcom.chu,lr[metadatas[17]]).group(1)
        except:
            lr[metadatas[21]] = ''
        try:
            lr[metadatas[22]] = re.search(wwwfangcom.yangtai,lr[metadatas[17]]).group(1)
        except:
            lr[metadatas[22]] = ''
        try:
            lr[metadatas[15]] = _split(fit_str, '建筑面积：', 1).split('使用面积：')[0].replace('O', '').replace('㎡','')
        except:
            lr[metadatas[15]] = ''
        try:
            lr[metadatas[16]] = _split(fit_str, '使用面积：', 1).split('O')[0].replace('O', '').replace('㎡','')
        except:
            lr[metadatas[16]] = ''
        if '年代' in lr[metadatas[16]]:
            lr[metadatas[16]] = ''
        try:
            dls = inforTxt_bs.find_all('dl')
            str_next_dl = (dls[1] if len(dls)>=2 else dls[0]).text
        except Exception as e:
            str_next_dl = ''
        lr[metadatas[9]] = _split(str_next_dl, '年代：', 1).split('年')[0].strip()
        #louceng = _split(str_next_dl.replace("）", ")"), '楼层：', 1).split(')')[0].strip()+')'
        try:
            louceng = re.search('楼层：([^)）]*[)）])', str_next_dl).group(1)
            lr[metadatas[11]] = louceng
            if '朝向：' in lr[metadatas[11]]:
                lr[metadatas[11]] = lr[metadatas[11]].split('朝向：')[0]
        except:
            lr[metadatas[11]] = ''
        try:
            lr[metadatas[12]] = re.findall('共(.*?)层',louceng,re.S)[0]
            lr[metadatas[13]] = re.findall('第(.*?)层',louceng,re.S)[0]
        except:
            lr[metadatas[12]] = ''
            lr[metadatas[13]] = ''

        lr[metadatas[30]] = _split(str_next_dl, '建筑类别：', 1).split('产权性质：')[0].strip()
        #lr[metadatas[27]] = _split(str_next_dl, '住宅类别：', 1).split('宅')[0].strip().replace(',','')+'宅'
        try:
            lr[metadatas[27]] = inforTxt_bs.find('span', text=re.compile(r'住宅类别：')).parent.getText(strip=True).replace('住宅类别：', '')
        except:
            lr[metadatas[27]] = ''
        lr[metadatas[28]] = _split(str_next_dl, '产权性质：', 1).split('楼盘名称：')[0].strip().replace(',','')
        lr[metadatas[29]] = _split(str_next_dl, '装修：', 1).split('住宅类别：')[0].strip()
        if '建筑类别：' in lr[metadatas[29]]:
            lr[metadatas[30]] = _split(lr[metadatas[29]], '装修情况：', 1).split('产权性质：')[0]
            lr[metadatas[28]] = _split(lr[metadatas[29]], '产权性质：', 1).split('楼盘名称：')[0]
            lr[metadatas[29]] = _split(lr[metadatas[29]], '建筑类别：', 0)
        elif '产权性质' in lr[metadatas[29]]:
            lr[metadatas[29]] = _split(lr[metadatas[29]], '产权性质：', 0)
        lr[metadatas[14]] = _split(str_next_dl,'朝向：',1).split('楼层：')[0].strip()
        # 地上层数
        try:
            lr[metadatas[55]] = inforTxt_bs.find('span', text=re.compile(r'地上层数：')).parent.getText(strip=True).replace('地上层数：', '').replace('层', '')
        except:
            lr[metadatas[55]] = ''
        try:
            lr[metadatas[58]] = inforTxt_bs.find('span', text=re.compile(r'车库数量：')).parent.getText(strip=True).replace('车库数量：', '').replace('个', '')
        except:
            lr[metadatas[58]] = ''
        if '地上层数' in lr[metadatas[14]]:
            #lr[metadatas[55]] = _split(lr[metadatas[14]], '地上层数：', 1).split('装修程度：')[0]
            lr[metadatas[56]] = _split(lr[metadatas[14]], '花园面积：', 1).split('车库数量：')[0]
            if '厅结构' in lr[metadatas[56]]:
                lr[metadatas[60]] = lr[metadatas[56]].split('厅结构：')[1].strip()
                if '车位数量：' in lr[metadatas[60]]:
                    lr[metadatas[60]] = _split(lr[metadatas[60]], '车位数量：', 0)
                lr[metadatas[56]] = lr[metadatas[56]].split('厅结构：')[0].strip()
            if '地下室面积：' in lr[metadatas[56]]:
                lr[metadatas[56]] = lr[metadatas[56]].split('地下室面积：')[0].strip()
            lr[metadatas[57]] = _split(lr[metadatas[14]], '地下室面积：', 1).split('楼盘名称：')[0]
            #lr[metadatas[58]] = _split(lr[metadatas[14]], '车库数量：', 1).split('车位数量：')[0]
            # if '楼盘名称：' in lr[metadatas[58]]:
            #     lr[metadatas[58]] = lr[metadatas[58]].split('楼盘名称：')[0].strip()
            lr[metadatas[59]] = _split(lr[metadatas[14]], '车位数量：', 1).split('地下室面积：')[0]
            if '楼盘名称：' in lr[metadatas[59]]:
                lr[metadatas[59]] = lr[metadatas[59]].split('楼盘名称：')[0].strip()
            lr[metadatas[29]] = _split(lr[metadatas[14]], '装修程度：', 1).split('建筑形式：')[0]
            if len(lr[metadatas[29]])>7:
                lr[metadatas[29]] = lr[metadatas[29]].split('修')[0].replace(',','')+'修'
            lr[metadatas[30]] = _split(lr[metadatas[14]], '建筑形式：', 1).split('面积：')[0]
            if '厅结构' in lr[metadatas[30]]:
                lr[metadatas[30]] = lr[metadatas[30]].split('厅结构：')[0]
            elif '车库数量' in lr[metadatas[30]]:
                lr[metadatas[30]] =lr[metadatas[30]].split('车库数量：')[0]
            elif '车位数量' in lr[metadatas[30]]:
                lr[metadatas[30]] = lr[metadatas[30]].split('车位数量：')[0]
            elif '地下室面积' in lr[metadatas[30]]:
                lr[metadatas[30]] = lr[metadatas[30]].split('地下室面积：')[0]
            elif '楼盘名称' in lr[metadatas[30]]:
                lr[metadatas[30]] = lr[metadatas[30]].split('楼盘名称：')[0]
            if '楼盘名称：' in lr[metadatas[30]]:
                lr[metadatas[30]] = lr[metadatas[30]].split('楼盘名称：')[0].strip()
            lr[metadatas[14]] = lr[metadatas[14]].split('地上层数')[0]
        elif '结构：' in lr[metadatas[14]]:
            lr[metadatas[14]] = lr[metadatas[14]].split('结构')[0]
        elif '装修：' in lr[metadatas[14]]:
            lr[metadatas[14]] = lr[metadatas[14]].split('装修')[0]
        elif '年代：' in lr[metadatas[14]]:
            lr[metadatas[14]] = lr[metadatas[14]].split('年代')[0]
        elif '小区：' in lr[metadatas[14]]:
            lr[metadatas[14]] = lr[metadatas[14]].split('小区')[0]
        if '楼层' in lr[metadatas[15]]:
            #150楼层：中层（共18层）朝向：南北装修：毛坯年代：2014年
            if '（共' in lr[metadatas[15]]:
                lr[metadatas[12]] = re.findall('（共(.*?)层',lr[metadatas[15]],re.S)[0]
                lr[metadatas[13]] = re.findall('楼层：(.*?)层',lr[metadatas[15]],re.S)[0]
                lr[metadatas[14]] = _split(lr[metadatas[15]], '朝向：', 1).split('装修：')[0]
                lr[metadatas[29]] = _split(lr[metadatas[15]], '装修：', 1).split('年代：')[0]
                lr[metadatas[9]] = _split(str_next_dl, '年代：', 1).split('年')[0].strip()
            lr[metadatas[15]] = lr[metadatas[15]].split('楼层')[0]
        if '朝向：' in lr[metadatas[15]]:
            lr[metadatas[15]] = lr[metadatas[15]].split('朝向')[0]
        if '地上层数：' in lr[metadatas[15]]:
            lr[metadatas[15]] = lr[metadatas[15]].split('地上层数')[0]
        try:
            if '装修：' in lr[metadatas[15]]:
                lr[metadatas[15]] = lr[metadatas[15]].split('装修')[0]
        except:pass
        if '建筑类别' in lr[metadatas[27]]:
            lr[metadatas[27]] = lr[metadatas[27]].split('建筑类别：')[0]
        if '产权性质' in lr[metadatas[27]]:
            lr[metadatas[27]] = lr[metadatas[27]].split('产权性质：')[0]
        if '建筑类别' in lr[metadatas[14]]:
            lr[metadatas[14]] = lr[metadatas[14]].split('建筑类别：')[0]
        if '小区：' in lr[metadatas[14]]:
            lr[metadatas[14]] = lr[metadatas[14]].split('小区：')[0]
        if '年代：' in lr[metadatas[14]]:
            lr[metadatas[14]] = lr[metadatas[14]].split('年代：')[0]
        if '楼盘名称：' in lr[metadatas[30]]:
            lr[metadatas[30]] = lr[metadatas[30]].split('楼盘名称：')[0]
        if '小区：' in lr[metadatas[29]]:
            lr[metadatas[29]] = lr[metadatas[29]].split('小区：')[0]
        if '年代：' in lr[metadatas[29]]:
            lr[metadatas[29]] = lr[metadatas[29]].split('年代：')[0]
        try:
            if '地下室面积：' in lr[metadatas[60]]:
                lr[metadatas[60]] = lr[metadatas[60]].split('地下室面积：')[0]
        except:pass

        try:
            if '楼盘名称：' in lr[metadatas[60]]:
                lr[metadatas[60]] = lr[metadatas[60]].split('楼盘名称：')[0]
        except:pass

        lr[metadatas[6]] = _split(str_next_dl, '楼盘名称：', 1).split('(')[0].strip() \
                           or ''.join(s.strip() for s in re.findall('小区：[^>]*>([^<]*)<', str(inforTxt_bs))) \
                           or _split(str_next_dl, '楼盘名称：', 1).replace("[地图交通]", '')

        try:
            lr[metadatas[3]] = _strip(city[3].string.replace('二手房', ''))
        except:
            lr[metadatas[3]] = ''
        lr[metadatas[48]] = _split(str_next_dl, '配套设施：', 1).strip()
        try:
            xqUrl_Bs = inforTxt_bs.dl.find_next('dl').find_all('a')
        except:
            xqUrl_Bs = ''
        try:
            lr[metadatas[7]] = _strip(xqUrl_Bs[0]['href'])
        except:
            lr[metadatas[7]] = ''
        try:
            xq_Bs = soup.find('div',attrs={'class': 'traffic mt10'})
        except:
            xq_Bs = ''
        try:
            lr[metadatas[8]] = _strip(xq_Bs.find('p').text.replace('地址：', ''))
        except Exception:
            lr[metadatas[8]] = ''
        try:
            lr[metadatas[47]] = _strip(xq_Bs.find('p').find_next('p').text.replace('交通状况：', ''))
        except:
            lr[metadatas[47]] = ''
        try:
            xqjj_Bs = soup.find('div', attrs={'class': 'introduct mt10'})
        except:
            xqjj_Bs = ''
        try:
            byjj = xqjj_Bs.find('span',class_='red20b').text
            lr[metadatas[25]] = _strip(byjj)
        except:
            lr[metadatas[25]] = ''
        try:
            all_xq_dd = xqjj_Bs.find_all('dd')
        except:
            all_xq_dd =[]

        try:
            lr[metadatas[31]] = _strip(all_xq_dd[2].text.strip().replace('物业类型：', ''))
        except:
            lr[metadatas[31]] = ''
        try:
            lr[metadatas[49]] = _strip(all_xq_dd[3].text.strip().replace('绿 化 率：', ''))
        except:
            lr[metadatas[49]] = ''
        try:
            lr[metadatas[51]] = _strip(all_xq_dd[4].text.strip().replace('物 业 费：', ''))
        except:
            lr[metadatas[51]] = ''
        try:
            lr[metadatas[50]] = _strip(all_xq_dd[5].text.strip().replace('物业公司：', ''))
        except:
            lr[metadatas[50]] = ''
        try:
            lr[metadatas[46]] = _strip(all_xq_dd[6].text.strip().replace('开 发 商：', ''))
        except:
            lr[metadatas[46]] = ''

        lr[metadatas[0]] = 's00000sf'
        lr[metadatas[66]] = 'sf'
        lr[metadatas[65]] = urlbase.order if urlbase.order is not None else ''

        lr[metadatas[10]] = ''
        lr[metadatas[26]] = ''
        lr[metadatas[32]] = ''
        lr[metadatas[42]] = ''
        lr[metadatas[43]] = ''
        lr[metadatas[44]] = ''
        lr[metadatas[45]] = ''
        lr[metadatas[52]] = ''
        lr[metadatas[53]] = ''
        lr[metadatas[54]] = ''
        lr[metadatas[62]] = ''
        lr[metadatas[63]] = ''
        lr[metadatas[64]] = ''
        for iitem in metadatas:
            try:
                lr[iitem]
            except:
                lr[iitem] = ''
        # print(metadatas[1], lr[metadatas[1]], '|',
        #       metadatas[2], lr[metadatas[2]], '|',
        #       metadatas[3], lr[metadatas[3]], '|',
        #       metadatas[6], lr[metadatas[6]], '|',
        #       metadatas[15], lr[metadatas[15]], '|',
        #       metadatas[23], lr[metadatas[23]], '|',
        #       metadatas[24], lr[metadatas[24]], '|',
        #       metadatas[37], lr[metadatas[37]])
        ###############################################
        #将分析的信息写入数据库
        # self.mysql.save(lr, metadatas)
        if lr[metadatas[1]].strip() == '':
            raise myException('数据错误,城市字段为空!')
        self.completionlr(lr, metadatas)
        MySqlEx.save(lr, metadatas)
    #def getinfo(self, urlbase):
        #LOG.info('fang8getinfo获得%s挂牌详细信息' , urlbase.url)


if __name__ == '__main__':
    wfang = wwwfangcom()
    # print(len(wfang.default(UrlBase('http://esf.hz.fang.com/newsecond/esfcities.aspx', 'wwwfangcom',order='123'))))
    # wfang.getpages(UrlBean('http://esf.binzhou.fang.com/house/h316-i36-j3100/', 'wwwsfcom#getitem', param=10, headers='哈尔滨',order='123'))
    # print(w58.getpages(UrlBean('http://bj.58.com/ershoufang/pn2', 'www58com#getitem', param=9, headers='北京')))
    wfang.getitem(UrlBean('http://esf.sh.fang.com/chushou/3_247454960.htm', 'wwwfangcom#getitem', param='北京',order='1234'))
    ls = (
'http://esf.tj.fang.com/chushou/3_191751219.htm',
'http://esf.sh.fang.com/chushou/3_245686871.htm',
'http://esf.sh.fang.com/chushou/3_245548373.htm',
'http://esf.hz.fang.com/chushou/3_178194568.htm',)
    for l in ls:
        wfang.getitem(UrlBean(l, 'wwwfangcom#getitem', param='北京',order='1234'))