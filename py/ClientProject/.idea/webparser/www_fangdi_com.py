#单例测试导入路径
if __name__ == '__main__':
    import sys, os
    parent_path = os.path.dirname(os.getcwd())
    sys.path.append(parent_path)

from util.UtilityGcs import GcsConverUtil
from webparser.webparserbase import ParserBase
from serializ.htmlfile import *
from serializ.oracle import *
from bean.urlbean import *
from log.logger import *
import datetime, json, copy
from random import random

LOG=logging.getLogger()
LOG.handlers[0].setLevel(logging.INFO)
LOG.handlers[1].setLevel(logging.INFO)

metadatas = ('省','城市','行政区','区域','街道路','路牌号','小区名','小区别名','楼栋名','楼栋别名',
             '楼栋街牌号','单元名','单元别名','单元街牌号','楼层名','楼层别名','房间名','房间别名','房间街牌号','小区坐标中心点坐标',
             '小区边界坐标','楼栋坐标','单元坐标','数据来源','开发商','总建筑面积','占地面积','房屋所有权证号','总户数','车位数量',
             '绿化率','容积率','总栋数','土地使用权证号','发证日期','地上层数','地下层数','建筑高度','规划用途','户型',
             '建筑面积','套内面积','公摊面积','按建面单价','按套内面单价','总价','朝向','小区id','小区评估系数','小区评估参数',
             '竣工年限','楼盘案例均价','楼栋id','建筑结构','房号','建筑类别','房屋结构','房屋户评估系数','扩展信息','STR_ORDER')

import requests, re
import urllib.parse
from bs4 import BeautifulSoup, Tag, NavigableString
from requests.exceptions import RequestException
class myException(Exception):pass

#解析上海网签数据
class wwwfangdicom(ParserBase):
    headers = {'Accept': '*/*',
               'Accept-Encoding': 'gzip, deflate',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36 LBBROWSER',
               'Connection': 'keep-alive',
               'Accept-Language':'zh-CN,zh;q=0.8',
               'Content-Type':'application/x-www-form-urlencoded;charset=gb2312'}
    htmlwrite = HtmlFile()

    page_patten = re.compile(r'共(\d*)页')
    pname_patten = re.compile(r'(?<=projectName=)([^&]*)')
    pid_patten = re.compile(r'(?<=projectID=)([^&]*)&?')

    def __init__(self):
        super(wwwfangdicom, self).__init__()

    #解析上海行政区列表
    def default(self, urlbase):
        LOG.info('上海网签获得行政区列表!')
        r = requests.get(urlbase.url, headers=self.headers, timeout=(5, 10))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('http状态:%s, url %s', r.status_code, urlbase.url)
            raise myException('http状态:%s, url %s' % (r.status_code, urlbase.url))
        soup = BeautifulSoup(r.content.decode('gbk', errors='ignore'), 'html.parser') #lxml
        se = soup.find("select", attrs=dict(name='districtID'))
        ls = []
        i_order = urlbase.order+'5'
        for op in se.find_all("option"):
            ls.append(UrlBean('http://www.fangdi.com.cn/complexPro.asp', self.message('getarea'), param={"districtID":op['value'], "buildingType":1, "imageField3.x":25, "imageField3.y":10}, headers=op.text.strip(), order=i_order))
            LOG.info('上海网签 %s 行政区', op.text)
            #area(s, dict(所属省份='上海直辖市', 所属城市='上海', 所属区域=op.text), "http://www.fangdi.com.cn/complexPro.asp", )
        return ls

    #解析行政区分页信息
    def getarea(self, urlbean):
        LOG.info('上海网签 %s %s', urlbean.headers, urlbean.param['districtID'])
        r = requests.post(urlbean.url, data=urlbean.param, headers=self.headers, timeout=(5, 10))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('http状态:%s, url %s', r.status_code, urlbean.url)
            raise myException('http状态:%s, url %s' % (r.status_code, urlbean.url))
        soup = BeautifulSoup(r.content.decode('gbk', errors='ignore'), 'html.parser') #lxml
        table = soup.find("table", id='Table7')
        LOG.info('%s:%s %s', urlbean.param['districtID'], urlbean.headers, re.sub(r'\[.*', '', table.getText(strip=True)))
        strUrl = '%s/%s' % ('/'.join(urlbean.url.split('/')[:3]), table.find('a', text=re.compile(r'下一页'))['href'])
        #解析总页数生成翻页任务
        ls = []
        i_order = urlbean.order[:-1]+'4'
        for page in range(int(re.search(self.page_patten, table.find_next(text=self.page_patten)).group(1))):
            sUrl = re.sub(r'page=(\d*)', ('page=%d' % (page+1)), strUrl)
            ls.append(UrlBean(sUrl, self.message('getpage'), headers=dict(xzq=urlbean.headers,page=page+1), order=i_order))
        return ls

    #解析行政区项目列表
    #@retries(10, delay=1, backoff=1, exceptions=(RequestException,myException))
    def getpage(self, urlbean):
        LOG.info('上海网签 %s %s', urlbean.headers['xzq'], urlbean.headers['page'])
        time.sleep(random()+1)
        r = requests.post(urlbean.url, headers=self.headers, timeout=(5, 10))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('http状态:%s, url %s', r.status_code, urlbean.url)
            raise myException('http状态:%s, url %s' % (r.status_code, urlbean.url))
        soup = BeautifulSoup(r.content.decode('gbk', errors='ignore'), 'html.parser') #lxml
        #解析项目列表
        ls = []
        i_order = urlbean.order[:-1]+'3'
        trs = soup.find_all('tr', attrs={"valign":"middle", "onmouseover":"javascript:this.bgColor='#A2E3F4';"})
        continue_indx = -1
        #根据项目ID与索引,进行断点续传,需要满足索引与项目ID匹配上
        if urlbean.param:
            if urlbean.param['pid'][:-10] in trs[urlbean.param['indx']].find('a')['href']:
                LOG.info('断点任务可继续')
                continue_indx = urlbean.param['indx']
            else:
                LOG.error('断点任务不可继续')
                raise myException('断点任务不可继续,%s %d页 %d个,项目id:%s,期望id:%s' % (urlbean.headers['xzq'], urlbean.headers['page'], urlbean.param['indx']+1, re.search(self.pid_patten, trs[urlbean.param['indx']].find('a')['href']).group(1), urlbean.param['pid']))

        for indx, tr in enumerate(trs):
            #跳过失败索引任务
            if indx<continue_indx:
                continue
            a = tr.find('a')
            #初始化抓取信息
            lr = {metadatas[58]:{}}
            lr[metadatas[0]] = lr[metadatas[1]] = '上海'
            lr[metadatas[2]] = urlbean.headers['xzq']
            if a:
                try:
                    lr[metadatas[25]] = a.parent.find_next('td').find_next('td').find_next('td').getText(strip=True)
                except:pass
                try:
                    lr[metadatas[28]] = a.parent.find_next('td').find_next('td').getText(strip=True)
                except:pass
                strUrl = '%s/%s' % ('/'.join(urlbean.url.split('/')[:3]), a['href'])
                LOG.info('%s %s', a.text, strUrl)
                #ls.append(UrlBean(strUrl, self.message('getproject'), param=lr, headers=a.text, order=i_order))
                #解析项目
                try:
                    self.getproject(UrlBean(strUrl, self.message('getproject'), param=lr, headers=a.text, order=i_order))
                except Exception as e:
                    #记录项目id与索引
                    pid = re.search(self.pid_patten, strUrl).group(1)
                    urlbean.param = dict(pid=pid, indx=indx)
                    raise myException('%s %d页 %d个 %s 项目异常!异常原因:%s' % (urlbean.headers['xzq'], urlbean.headers['page'], indx+1, a.text, str(e)))
            else:
                LOG.error('上海网签 %s 无有效连接!', tr.getText(strip=True))
        return ls

    #解析项目
    #@retries(10, delay=1, backoff=1, exceptions=(RequestException,myException))
    def getproject(self, urlbean):
        LOG.info('上海网签 %s', urlbean.headers)
        time.sleep(random()+1)
        r = requests.post(urlbean.url, headers=self.headers, timeout=(5, 10))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('http状态:%s, url %s', r.status_code, urlbean.url)
            raise myException('http状态:%s, url %s' % (r.status_code, urlbean.url))
        soup = BeautifulSoup(r.content.decode('gbk', errors='ignore'), 'html.parser') #lxml
        ###########################################################################################
        lr = urlbean.param
        try:
            lr[metadatas[3]] = re.sub(r'板块$', '', soup.find('td', text=re.compile(r'所属板块：')).find_next('td').getText(strip=True))
        except:pass
        try:
            lr[metadatas[4]] = soup.find('td', text=re.compile(r'项目地址：')).find_next('td').getText(strip=True)
        except:pass
        try:
            lr[metadatas[6]] = soup.find('td', text=re.compile(r'项目名称：')).find_next('td').getText(strip=True)
        except:pass
        try:
            lr[metadatas[19]] = lr[metadatas[20]] = self.getbaidugcs(lr[metadatas[6]], lr[metadatas[1]])
        except:pass
        lr[metadatas[23]] = urlbean.url
        #可抓取企业扩展信息
        try:
            lr[metadatas[24]] = soup.find('td', text=re.compile(r'企业名称：')).find_next('td').getText(strip=True)
        except:pass
        #进入企业信息页面
        if soup.find('td', text=re.compile(r'企业名称：')).find_next('td').find('a'):
            qyurl = '%s/%s' % ('/'.join(urlbean.url.split('/')[:3]), soup.find('td', text=re.compile(r'企业名称：')).find_next('td').find('a')['href'])
            lr[metadatas[58]]['企业链接'] = qyurl
            time.sleep(random()+1)
            r_qy = requests.get(qyurl, headers=self.headers, timeout=(5, 10))
            LOG.info('访问耗时:%.4f, url:%s', r_qy.elapsed.microseconds/1000000, r_qy.url)
            if(r_qy.status_code != requests.codes.ok):
                LOG.warning('http状态:%s, url %s', r_qy.status_code, qyurl)
                raise myException('http状态:%s, url %s' % (r_qy.status_code, qyurl))
            soup_qy = BeautifulSoup(r_qy.content.decode('gbk', errors='ignore'), 'html.parser') #lxml
            try:
                lr[metadatas[58]]['编号'] = soup_qy.find('td', text=re.compile(r'企业基本信息')).getText(strip=True).split('编号:')[1]
            except:pass
            for key in ('法人代表', '总经理', '企业类型', '电子邮件', '电话', '传真', '邮政编码', '经营地址',
                        '资质等级', '资质证编号', '资质发证日', '批准从事房地产日期', '注册类型', '资质有效期',
                        '营业执照编号', '经营范围', '工商注册日', '执照到期日', '注册资本', '注册地址',
                        '专业人员', '在册人员', '高级职称', '中级职称', '初级职称'):
                try:
                    lr[metadatas[58]][key] = soup_qy.find('td', text=re.compile(key)).find_next('td').getText(strip=True)
                    if key == '注册资本':
                        lr[metadatas[58]][key] = re.sub(r'[，,万]*', '', lr[metadatas[58]][key])
                except:pass
        #解析楼盘介绍
        if soup.find('a', text=re.compile(r'点击查看楼盘介绍')):
            lpurl = '%s/%s' % ('/'.join(urlbean.url.split('/')[:3]), soup.find('a', text=re.compile(r'点击查看楼盘介绍'))['href'])
            lr[metadatas[58]]['楼盘链接'] = lpurl
            time.sleep(random()+1)
            r_lp = requests.get(lpurl, headers=self.headers, timeout=(5, 10))
            LOG.info('访问耗时:%.4f, url:%s', r_lp.elapsed.microseconds/1000000, r_lp.url)
            if(r_lp.status_code != requests.codes.ok):
                LOG.warning('http状态:%s, url %s', r_lp.status_code, lpurl)
                raise myException('http状态:%s, url %s' % (r_lp.status_code, lpurl))
            soup_lp = BeautifulSoup(r_lp.content.decode('gbk', errors='ignore'), 'html.parser') #lxml
            try:
                lr[metadatas[29]] = re.sub(r'[^\d.]+', '', soup_lp.find('td', text=re.compile(r'车\s*位：')).find_next('td').getText(strip=True))
            except:pass
            try:
                lr[metadatas[30]] = re.sub(r'[^\d.]+', '', soup_lp.find('td', text=re.compile(r'绿\s*化\s*率：')).find_next('td').getText(strip=True))
            except:pass
            try:
                lr[metadatas[31]] = re.sub(r'[^\d.]+', '', soup_lp.find('td', text=re.compile(r'容\s*积\s*率：')).find_next('td').getText(strip=True))
            except:pass
            for key in ('楼盘简介：', '设备装修：', '施工进度：', '配套设施：', '周围交通：',
                        '交通位置：', '开盘时间：', '入住时间：'):
                try:
                    lr[metadatas[58]][key] = soup_lp.find('td', text=re.compile(key)).find_next('td').getText(strip=True)
                except:pass
            try:
                lr[metadatas[58]]['类型'] = soup_lp.find('td', text=re.compile('类\s*型：')).find_next('td').getText(strip=True)
            except:pass
            try:
                lr[metadatas[58]]['备注'] = soup_lp.find('td', text=re.compile('备\s*注：')).find_next('td').getText(strip=True)
            except:pass
        try:
            lr[metadatas[43]] = re.sub(r'[，,元]*', '', soup.find('td', text=re.compile(r'累计合同均价')).find_next('td').find_next('td').getText(strip=True))
        except:pass
        try:
            lr[metadatas[58]]['累计住宅合同均价'] = re.sub(r'[，,元]*', '', soup.find('td', text=re.compile(r'累计住宅合同均价')).find_next('td').find_next('td').getText(strip=True))
        except:pass
        #解析预售许可证
        iframe = soup.find('iframe', id='SUList')
        time.sleep(random()+1)
        resp = requests.get('%s/%s' % ('/'.join(urlbean.url.split('/')[:3]), iframe['src']), headers=self.headers, timeout=(5, 1.5))
        if(resp.status_code != requests.codes.ok):
            LOG.warning('http状态:%s, url %s', r.status_code, urlbean.url)
            raise myException('http状态:%s, url %s' % (r.status_code, urlbean.url))
        rsoup = BeautifulSoup(resp.content.decode('gbk', errors='ignore'), 'html.parser')
        table = rsoup.find('table')
        #预售许可
        ls = []
        i_order = urlbean.order[:-1]+'2'
        for a in table.find_all('a'):
            strUrl = '%s/%s' % ('/'.join(urlbean.url.split('/')[:3]), a['href'])
            LOG.info('上海网签 %s %s', urlbean.headers, a.text)
            #将预售证信息作为参数放在下一步存储,这里就省去了拷贝lr
            #ls.append(UrlBean(strUrl, self.message('getld'), param=lr, headers=a.text, order=i_order))
            self.getld(UrlBean(strUrl, self.message('getld'), param=lr, headers=a.text, order=i_order))
        return ls

    #解析楼栋
    #@retries(10, delay=1, backoff=1, exceptions=(RequestException,myException))
    def getld(self, urlbean):
        LOG.info('上海网签 %s', urlbean.headers)
        time.sleep(random()+1)
        r = requests.post(urlbean.url, headers=self.headers, timeout=(5, 10))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('http状态:%s, url %s', r.status_code, urlbean.url)
            raise myException('http状态:%s, url %s' % (r.status_code, urlbean.url))
        soup = BeautifulSoup(r.content.decode('gbk', errors='ignore'), 'html.parser') #lxml
        #楼栋
        table = soup.find('table')
        ls = []
        i_order = urlbean.order[:-1]+'1'
        for a in table.find_all('a'):
            lr = copy.deepcopy(urlbean.param)
            lr[metadatas[8]] = lr[metadatas[10]] = a.getText(strip=True)
            lr[metadatas[27]] = urlbean.headers
            #获得楼栋报价
            try:
                lr[metadatas[58]]['楼栋报价'] = a.parent.find_next('td').getText(strip=True)
            except:
                raise myException('getld parent error!'+r.content.decode('gbk', errors='ignore')[:500])
            #处理项目中文参数编码
            try:
                pname = urllib.parse.unquote(re.search(self.pname_patten, a['href']).group(1), encoding='utf8')
                purl = re.sub(self.pname_patten, urllib.parse.quote(pname, encoding='gbk'), a['href'])
            except:
                purl = a['href']
            #替换项目参数并重新组装URL地址
            strUrl = '%s/%s' % ('/'.join(urlbean.url.split('/')[:3]), purl)
            LOG.info('上海网签 %s %s', urlbean.headers, a.text)
            #ls.append(UrlBean(strUrl, self.message('getitem'), param=lr, headers=a.text, order=i_order))
            self.getitem(UrlBean(strUrl, self.message('getitem'), param=lr, order=i_order))
        return ls

    #解析项目列表
    #@retries(10, delay=1, backoff=1, exceptions=(RequestException,myException))
    def getitem(self, urlbean):
        LOG.info('上海网签 %s %s 获得到户信息', urlbean.param[metadatas[6]], urlbean.param[metadatas[8]])
        time.sleep(random()+1)
        r = requests.get(urlbean.url, headers=self.headers, timeout=(5, 20))
        if(r.status_code != requests.codes.ok):
            LOG.warning('http状态:%s, url %s', r.status_code, urlbean.url)
            raise myException('http状态:%s, url %s' % (r.status_code, urlbean.url))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        #存储页面信息

        self.htmlwrite.save('%s\\%s\\%s' % (self.__class__.__name__, self.duefname(urlbean.param[metadatas[2]]), self.duefname(urlbean.param[metadatas[6]])), self.duefname(urlbean.param[metadatas[8]]), r.content.decode('gbk'))
        t1 = time.time()
        soup = BeautifulSoup(r.content.decode('gbk', errors='ignore'), 'html.parser') #lxml
        #解析数据
        td = soup.find('td', text=re.compile('室号'))
        try:
            table = td.parent.parent.parent.parent.parent
        except:
            raise myException('getitem parent error!'+r.content.decode('gbk', errors='ignore')[:500])
        trs = list(filter(lambda x:isinstance(x, Tag), table.children))[1:]
        lr = urlbean.param
        #批号
        lr[metadatas[59]] = urlbean.order[:-1]+'0'
        #填充为空的字段
        self.completionlr(lr, metadatas)
        ls = []
        for tr in trs:
            for indx, td in enumerate(tr.find_all('td')):
                if indx==0:
                    #print("楼层名", td.getText(strip=True))
                    lr[metadatas[14]] = td.getText(strip=True)
                    continue
                else:
                    dr = copy.deepcopy(lr)
                    #print("房间号", td.getText(strip=True))
                    #抓取房间号面积
                    dr[metadatas[16]] = td.getText(strip=True)
                    dr[metadatas[54]] = ''.join(re.sub(r'[^\d.]+', '-', dr[metadatas[16]]).strip('-').split('-')[-1:])
                    try:
                        dr[metadatas[40]] = re.search(r'实测面积[：:]?([0-9.]*)',td['title']).group(1)
                    except:pass
                    try:
                        dr[metadatas[58]]['预测面积'] = re.search(r'预测面积[：:]?([0-9.]*)',td['title']).group(1)
                    except:pass
                    #print(td['title'])
                    #判断是否有到户链接
                    if td.find('a'):
                        try:
                            rh_url = '%s/%s' % ('/'.join(urlbean.url.split('/')[:3]), td.find('a')['href'])
                            time.sleep(random()+1)
                            rh = requests.get(rh_url, headers=self.headers, timeout=(5, 5))
                            if(rh.status_code != requests.codes.ok):
                                LOG.warning('http状态:%s, url %s', r.status_code, urlbean.url)
                                raise myException('http状态:%s, url %s' % (r.status_code, urlbean.url))
                            #LOG.info('访问耗时:%.4f, url:%s', rh.elapsed.microseconds/1000000, rh.url)
                            souph = BeautifulSoup(rh.content.decode('gbk', errors='ignore'), 'html.parser')
                            dr[metadatas[58]]['房屋链接'] = urlbean.url
                            #抓取户型信息
                            try:
                                dr[metadatas[38]] = souph.find('td', text=re.compile('房屋类型')).nextSibling.nextSibling.text
                            except:pass
                            try:
                                dr[metadatas[39]] = souph.find('td', text=re.compile('房型')).nextSibling.nextSibling.text
                            except:pass
                            try:
                                dr[metadatas[41]] = souph.find('td', text=re.compile('实测套内面积')).nextSibling.nextSibling.text
                            except:pass
                            try:
                                dr[metadatas[42]] = souph.find('td', text=re.compile('实测分摊面积')).nextSibling.nextSibling.text
                            except:pass
                            #扩展信息
                            for k in ('预测套内面积', '预测分摊面积', '预测地下面积',
                                      '实测地下面积', '状态'):
                                try:
                                    dr[metadatas[58]][k] = souph.find('td', text=re.compile(k)).nextSibling.nextSibling.text
                                except:pass
                        except:pass
                    dr[metadatas[58]] = json.dumps(dr[metadatas[58]], ensure_ascii=False)
                    ls.append(dr)
        t2 = time.time()
        LOG.info('解析页面耗时:%f' % (t2-t1))
        #print(self.getbaidugcs('中福花苑二期', '上海'))
        #存储
        MySqlEx.savewq(ls, metadatas)


if __name__ == '__main__':
    wfd = wwwfangdicom()
    for area in wfd.default(UrlBase('http://www.fangdi.com.cn/NewSale.htm', 'wwwfangdicom', order='0123456789')):
        for page in wfd.getarea(area)[:2]:
            for project in wfd.getpage(page)[:2]:
                for ysz in wfd.getproject(project)[:2]:
                    for ld in wfd.getld(ysz)[:2]:
                        wfd.getitem(ld)

    # for area in wfd.default(UrlBase('http://www.fangdi.com.cn/NewSale.htm', 'wwwfangdicom', order='0123456789')):
    #     for page in wfd.getarea(area)[:1]:
    #         #测试断点续传
    #         page.param = dict(pid='Mjk1N3wyMDE2LTYtNHw1Mg==', indx=1)
    #         try:
    #             wfd.getpage(page)
    #         except Exception as e:
    #             print(page.param)
    #             print(str(e))
    #             raise

    #wfd.default(UrlBase('http://www.fangdi.com.cn/NewSale.htm', 'wwwfangdicom', order='0123456789'))
    #wfd.getarea(UrlBean('http://www.fangdi.com.cn/complexPro.asp', 'wwwfangdicom#getarea', param='上海',order='0123456789'))
    #wfd.getpage(UrlBean('http://www.fangdi.com.cn/complexpro.asp?page=1&districtID=1&Region_ID=&projectAdr=&projectName=&startCod=&buildingType=1&houseArea=0&averagePrice=0&selState=&selCircle=0', 'wwwfangdicom#getpage', headers={'xzq':'黄浦区', 'page':1}, order='0123456789'))
    #wfd.getproject(UrlBean('http://www.fangdi.com.cn/proDetail.asp?projectID=ODI3NHwyMDE2LTUtMjZ8MTE=', 'wwwfangdicom#getproject', param={metadatas[58]:{}}, headers='中福花苑二期', order='0123456789'))
    #wfd.getld(UrlBean('http://www.fangdi.com.cn/building.asp?ProjectID=NjA0MXwyMDE2LTUtMjh8NTE=&projectName=%E6%B9%96%E7%95%94%E4%BD%B3%E8%8B%91%E4%B8%89%E6%9C%9F&PreSell_ID=13038&Start_ID=12992', 'wwwfangdicom#getld', param={metadatas[58]:{}}, headers='中山南路1358弄15号', order='0123456789'))
    #wfd.getitem(UrlBean('http://www.fangdi.com.cn/House.asp?ProjectID=ODI3NHwyMDE2LTUtMjZ8MTE=%D6%D0%B8%A3%BB%A8%D4%B7%B6%FE%C6%DAPreSell_ID=15377&Start_ID=15303&bname=%D6%D0%C9%BD%C4%CF%C2%B71358%C5%AA15%BA%C5&Param=MjUwMjc5ODU1MXx8MjAxNi01LTI2IDExOjU3OjE5fHwx&flag=MQ==', 'wwwfangdicom#getitem', param={metadatas[58]:{}}, headers='中山南路1358弄15号', order='0123456789'))


    #ls = ('http://yb.58.com/ershoufang/22105173561892x.shtml',
# 'http://bj.58.com/ershoufang/26024442826063x.shtml',
# 'http://zw.58.com/ershoufang/26029042996409x.shtml',
# 'http://huizhou.58.com/ershoufang/25864472115792x.shtml',
# 'http://xj.58.com/ershoufang/25982128259243x.shtml',
# 'http://wx.58.com/ershoufang/25923357493551x.shtml',
# 'http://nc.58.com/ershoufang/25988379792185x.shtml',
# 'http://wh.58.com/ershoufang/25976106912317x.shtml',
# 'http://xm.58.com/ershoufang/25977780194114x.shtml',
# 'http://bt.58.com/ershoufang/25968667225911x.shtml'
# )
#
#     for l in ls:
#         w58.getitem(UrlBean(l, 'wwwfangcom#getitem', param='北京',order='1234'))
    # cs = w58.default(UrlBase('http://www.58.com/ershoufang/changecity/', 'www58com',order='123450'))
    # for c in cs:
    #     for idx, item in enumerate(w58.getpages(c)):
    #         #w58.getitem(item)
    #         #print(idx+1, item.headers, item.url)
    #         print(item.url)
