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

import requests, re, urllib.parse
from urllib.parse import urlencode
from bs4 import BeautifulSoup, Tag, NavigableString
class myException(Exception):pass

#解析郑州网签数据
class wwwzzfdccomcn(ParserBase):
    headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36 LBBROWSER', 'Connection': 'keep-alive'}
    htmlwrite = HtmlFile()


    page_patten = re.compile(r'共(\d*)页')
    pname_patten = re.compile(r'(?<=LpName=)([^&]*)')
    ysz_patten = re.compile(r'(?<=yszhNum=)([^&]*)')
    PALD = re.compile(r'WaitQuery\(\'([^\']*)\',\'([^\']*)\',\'([^\']*)\',\'([^\']*)\'\)')

    def __init__(self):
        super(wwwzzfdccomcn, self).__init__()

    #解析上海行政区列表
    def default(self, urlbase):
        LOG.info('郑州网签列表!')
        #http://www.zzfdc.gov.cn/spfcs/search.do?act=xiangmu&ZH=&QUYU=全部&KFS=&MCDZ=项目名称&INPUT_MCDZ=&make=&B1222=查询项目
        params = urlencode(dict(act='xiangmu', ZH='', QUYU='全部', KFS='',
                                MCDZ='项目名称', INPUT_MCDZ='', make='',
                                B1222='查询项目'), doseq=True, encoding='gbk')
        sUrl = '%s?%s' % (urlbase.url, params)
        r = requests.get(sUrl, headers=self.headers, timeout=(3.05, 10))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('http状态:%s, url %s', r.status_code, urlbase.url)
            raise myException('http状态:%s, url %s' % (r.status_code, urlbase.url))
        soup = BeautifulSoup(r.content.decode('gbk', errors='ignore'), 'html.parser') #lxml
        a = soup.find('a', text=re.compile(r'下一页'))
        pages = re.search(self.page_patten, a.parent.getText(strip=True)).group(1)
        ls = []
        i_order = urlbase.order+'0'
        pageUrl = '%s%s' % ('/'.join(urlbase.url.split('/')[:3]), a['href'])
        for page in range(int(pages)):
            #http://www.zzfdc.gov.cn/spfcs/search.do?method=queryWithPage&pageMethod=next&ZH=&KFS=&INPUT_MCDZ=&currentPage=0&act=xiangmu&MCDZ=项目名称&QUYU=全部
            ls.append(UrlBean(re.sub(r'(?<=currentPage=)(\d*)', str(page), pageUrl), self.message('getpage'), headers=str(page+1), order=i_order))
            LOG.info('郑州网签 第%d页', page+1)
        return ls

    #解析行政区分页信息
    def getpage(self, urlbean):
        LOG.info('郑州网签 第%s页', urlbean.headers)
        time.sleep(random()+1)
        r = requests.get(urlbean.url, headers=self.headers, timeout=(3.05, 10))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('http状态:%s, url %s', r.status_code, urlbean.url)
            raise myException('http状态:%s, url %s' % (r.status_code, urlbean.url))
        soup = BeautifulSoup(r.content.decode('gbk', errors='ignore'), 'html.parser') #lxml
        #解析列表
        ls = []
        i_order = urlbean.order[:-1]+'1'
        #去掉表头和表尾
        for tr in soup.find('span', text=re.compile(r'楼盘')).find_parent('table').find_all('tr')[1:-1]:
            strUrl = '%s%s' % ('/'.join(urlbean.url.split('/')[:3]), tr.find('a')['href'])
            ls.append(UrlBean(strUrl, self.message('getproject'), headers=dict(page=urlbean.headers, pname=tr.find('a').getText(strip=True)), order=i_order))
        return ls

    #解析项目
    def getproject(self, urlbean):
        LOG.info('郑州网签 第%s页 %s', urlbean.headers['page'], urlbean.headers['pname'])
        time.sleep(random()+1)
        r = requests.post(urlbean.url, headers=self.headers, timeout=(3.05, 10))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('http状态:%s, url %s', r.status_code, urlbean.url)
            raise myException('http状态:%s, url %s' % (r.status_code, urlbean.url))
        soup = BeautifulSoup(r.content.decode('gbk', errors='ignore'), 'html.parser') #lxml
        #解析项目列表
        ls = []
        i_order = urlbean.order[:-1]+'2'
        #初始化抓取信息
        lr = {metadatas[58]:{}}
        lr[metadatas[0]] = '河南'
        lr[metadatas[1]] = '郑州'
        try:
            lr[metadatas[2]] = soup.find('td', text=re.compile(r'域：')).next_sibling.next_sibling.getText(strip=True)
        except:pass
        try:
            lr[metadatas[4]] = soup.find('td', text=re.compile(r'地理位置：')).next_sibling.next_sibling.text
        except:pass
        try:
            lr[metadatas[6]] = soup.find('td', text=re.compile(r'楼盘名称：')).next_sibling.next_sibling.getText(strip=True)
        except:pass
        try:
            lr[metadatas[19]] = lr[metadatas[20]] = self.getbaidugcs(lr[metadatas[6]], lr[metadatas[1]])
        except:pass
        try:
            lr[metadatas[24]] = soup.find('td', text=re.compile(r'商：')).next_sibling.next_sibling.text
        except:pass
        try:
            lr[metadatas[31]] = soup.find(text=re.compile(r'容积率：?')).find_parent('td').next_sibling.next_sibling.text
        except:pass
        try:
            lr[metadatas[53]] = soup.find(text=re.compile(r'建筑结构：?')).find_parent('td').next_sibling.next_sibling.text
        except:pass
        try:
            lr[metadatas[30]] = soup.find(text=re.compile(r'绿化率：?')).find_parent('td').next_sibling.next_sibling.text
        except:pass
        try:
            lr[metadatas[33]] = soup.find(text=re.compile(r'国有土地使用证：?')).find_parent('td').next_sibling.next_sibling.text
        except:pass
        # try:
        #     lr[metadatas[58]]['预售证链接'] = [a['href'] for a in soup.find('td', text=re.compile(r'预\s*售\s*证：?')).find_next('td').find_all('a')]
        # except:pass
        #扩展信息
        for key in ('销售热线', '公司网址'):
            try:
                lr[metadatas[58]][key] = soup.find('td', text=re.compile(r'%s：?' % key)).next_sibling.next_sibling.text
            except:pass
        for key in ('开盘时间', '进驻时间', '售楼处',
                    '物业公司', '交付标准', '物业标准',
                    '建设工程规划许可证', '建设用地规划许可证', '施工许可证'):
            try:
                lr[metadatas[58]][key] = soup.find(text=re.compile(r'%s：?' % key)).find_parent('td').next_sibling.next_sibling.text
            except:pass
        #抓取开发商信息
        #楼盘档案
        #http://www.zzfdc.gov.cn/spfcs/showLp.do?showType=Lpdn&LpName=宏江瀚苑&LpId=1168
        #开发商
        #http://www.zzfdc.gov.cn/spfcs/showLp.do?showType=Kfs&LpName=宏江瀚苑&LpId=1168
        #楼盘表
        #http://www.zzfdc.com.cn/sw/spfmanager.do?act=showLp&showType=Lpb&LpName=宏江瀚苑&LpId=1168

        # 通过iframe来获取地址不仅麻烦还浪费一次url请求和解析时间,改为直接拼接地址
        iframeurl = '%s/%s' % ('/'.join(urlbean.url.split('/')[:4]), soup.find('iframe')['src'])
        iframeurl = re.sub(self.pname_patten, lambda x:urllib.parse.quote(x.group(0), encoding='gbk'), iframeurl)
        time.sleep(random()+1)
        iframe_r = requests.get(iframeurl, headers=self.headers, timeout=(3.05, 10))
        LOG.info('访问耗时:%.4f, url:%s', iframe_r.elapsed.microseconds/1000000, iframeurl)
        if(iframe_r.status_code != requests.codes.ok):
            LOG.warning('http状态:%s, url %s', iframe_r.status_code, iframeurl)
            raise myException('http状态:%s, url %s' % (iframe_r.status_code, iframeurl))
        iframe_soup = BeautifulSoup(iframe_r.content.decode('gbk', errors='ignore'), 'html.parser')

        kfsurl = '%s/%s' % ('/'.join(urlbean.url.split('/')[:4]), iframe_soup.find('a', text=re.compile(r'开发商'))['href'])
        kfsurl = re.sub(self.pname_patten, lambda x:urllib.parse.quote(x.group(0), encoding='gbk'), kfsurl)

        time.sleep(random()+1)
        kfs_r = requests.get(kfsurl, headers=self.headers, timeout=(3.05, 10))
        LOG.info('访问耗时:%.4f, url:%s', kfs_r.elapsed.microseconds/1000000, kfsurl)
        if(kfs_r.status_code != requests.codes.ok):
            LOG.warning('http状态:%s, url %s', kfs_r.status_code, kfsurl)
            raise myException('http状态:%s, url %s' % (kfs_r.status_code, kfsurl))
        kfs_soup = BeautifulSoup(kfs_r.content.decode('gbk', errors='ignore'), 'html.parser')
        for key in ('法人代表', '电话', '联系人', '邮政编码', '经营地址',
                    '资质等级', '资质证编号', '资质发证日', '经营范围',
                    '营业执照编号', '注册地址', '注册资本'):
            try:
                lr[metadatas[58]][key] = kfs_soup.find(text=re.compile(r'%s[:：]?' % key)).find_parent('td').find_next('td').text
            except:
                print(key)
        #抓楼盘表,存在小区没有楼盘表的情况会返回404错误,这个就生成一个空记录存储小区信息
        lpburl = iframe_soup.find('a', text=re.compile(r'楼盘表'))['href']
        lpburl = re.sub(self.pname_patten, lambda x:urllib.parse.quote(x.group(0), encoding='gbk'), lpburl)
        lpburl = re.sub(self.ysz_patten, lambda x:urllib.parse.quote(x.group(0), safe=',', encoding='gbk'), lpburl)
        time.sleep(random()+1)
        lpb_r = requests.get(lpburl, headers=self.headers, timeout=(3.05, 10))
        LOG.info('访问耗时:%.4f, url:%s', lpb_r.elapsed.microseconds/1000000, lpburl)
        #生成楼栋信息
        i_order = urlbean.order[:-1]+'2'
        ls = []
        if(lpb_r.status_code == requests.codes.ok):
            #解析楼盘表
            lpb_soup = BeautifulSoup(lpb_r.content.decode('utf8', errors='ignore'), 'html.parser')
            lpburl = lpb_soup.find('iframe')['src']
            time.sleep(random()+1)
            lpb_r = requests.get(lpburl, headers=self.headers, timeout=(3.05, 10))
            LOG.info('访问耗时:%.4f, url:%s', lpb_r.elapsed.microseconds/1000000, lpburl)
            if(lpb_r.status_code != requests.codes.ok):
                LOG.warning('http状态:%s, url %s', lpb_r.status_code, lpburl)
                raise myException('http状态:%s, url %s' % (lpb_r.status_code, lpburl))
            lpb_soup = BeautifulSoup(lpb_r.content.decode('gbk', errors='ignore'), 'html.parser')
            lr[metadatas[28]] = lpb_soup.find('td', text=re.compile(r'总套\(间\)数：')).find_next('td').text.replace('套', '')
            lr[metadatas[26]] = lpb_soup.find('td', text=re.compile(r'总面积：')).find_next('td').text.replace('m2', '')
            lr[metadatas[43]] = lpb_soup.find('td', text=re.compile(r'已售房屋平均价：')).find_next('td').text.replace('元/m2', '')
            lr[metadatas[51]] = lpb_soup.find('td', text=re.compile(r'销售房屋平均价：')).find_next('td').text.replace('元/m2', '')
            for key in ('当前可售套(间)数', '认购套数', '认购面积', '作废率', '销售套数'):
                try:
                    lr[metadatas[58]][key] = re.sub(r'套|(m2)|(元/m2)|', '', lpb_soup.find('td', text=re.compile(r'%s[:：]?' % key.replace('(', '\(').replace(')', '\)'))).find_next('td').text)
                except:pass
            for tr in lpb_soup.find('td', text=re.compile(r'楼栋名称')).find_parent('table').find_all('tr', attrs=dict(bgcolor='#F7F7F7')):
                dr = copy.deepcopy(lr)
                dr[metadatas[8]] = tr.find_all('td')[0].getText(strip=True)
                dr[metadatas[53]] = tr.find_all('td')[4].text
                try:
                    dr[metadatas[58]]['楼栋可售套数'] = tr.find_all('td')[1].text
                except:pass
                try:
                    dr[metadatas[58]]['楼栋总套数'] = tr.find_all('td')[2].text
                except:pass
                try:
                    dr[metadatas[58]]['楼栋认购数'] = tr.find_all('td')[3].text
                except:pass
                try:
                    dr[metadatas[58]]['预售证号'] = tr.find_all('td')[5].getText(strip=True)
                except:pass
                try:
                    self.getysz(dr, dr[metadatas[58]]['预售证号'])
                except:pass
                gs = re.search(self.PALD, tr.find('td')['onclick']).groups()
                ldurl = 'http://www.zzfdc.gov.cn:8000/360fcservice2011/spfcs/showLp.do?showType=Fz&LpId=%s&yszhNum=%s&LpName=%s&lfNum=%s' % (gs[0], gs[1], urllib.parse.quote( dr['小区名'] if gs[2]=='null' else gs[2], encoding='gbk'), urllib.parse.quote(gs[3], encoding='gbk'))
                ls.append(UrlBean(ldurl, self.message('getitem'), param=dr, order=i_order))
            return ls
        elif lpb_r.status_code == 404:
            #无楼盘表信息,生成一个小区记录
            #记录小区的预售信息
            try:
                ysz_set = set()
                for ysz_a in soup.find('td', text=re.compile(r'\s*预\s*售\s*证[：:]?')).find_next('td').find_all('a'):
                    try:
                        for id in urllib.parse.parse_qs(ysz_a['href'].split('?')[-1])['id']:
                            ysz_set.add(id)
                    except:
                        LOG.error('解析预售证ID失败, url:%s', ysz_a['href'])
                        raise myException('解析预售证ID失败, url:%s' % ysz_a['href'])
                if ysz_set:
                    lr[metadatas[58]]['预售证号'] = ','.join(ysz_set)
                #请求预售证信息
                if len(ysz_set)==1:
                    try:
                        ysz_id = ysz_set.pop()
                        self.getysz(lr, ysz_id)
                    except Exception as e:
                        LOG.error('预售证抓取失败, 预售证id:%s, 异常类型:%s, 异常信息:%s', ysz_id, type(e), str(e))
                        raise myException('预售证抓取失败, 预售证id:%s, 异常类型:%s, 异常信息:%s' % (ysz_id, type(e), str(e)))
                elif len(ysz_set)>1:
                    lr[metadatas[58]]['预售证列表'] = []
                    for ysz_id in ysz_set:
                        try:
                            ysz_dict = {metadatas[58]:{}}
                            self.getysz(ysz_dict, ysz_id)
                            ysz_dict.update(ysz_dict[metadatas[58]])
                            del ysz_dict[metadatas[58]]
                            lr[metadatas[58]]['预售证列表'].append(ysz_dict)
                        except Exception as e:
                            LOG.error('预售证抓取失败, 预售证id:%s, 异常类型:%s, 异常信息:%s', ysz_id, type(e), str(e))
                            raise myException('预售证抓取失败, 预售证id:%s, 异常类型:%s, 异常信息:%s' % (ysz_id, type(e), str(e)))
            except Exception as e:
                LOG.error('预售证抓取失败,异常类型%s,异常信息%s', type(e), str(e))
                raise myException('预售证抓取失败,异常类型%s,异常信息%s' % (type(e), str(e)))
            #填充为空的字段
            self.completionlr(lr, metadatas)
            #存储
            lr[metadatas[58]] = json.dumps(lr[metadatas[58]], ensure_ascii=False)
            lr[metadatas[59]] = i_order
            MySqlEx.savewq([lr], metadatas)
            return ls
        else:
            LOG.warning('http状态:%s, url %s', lpb_r.status_code, lpburl)
            raise myException('http状态:%s, url %s' % (lpb_r.status_code, lpburl))

    #解析预售证
    def getysz(self, lr, ysznum):
        url = 'http://www.zzfdc.gov.cn/xinyuchaxun/newlistone.jsp?id=%s' % (ysznum.strip())
        time.sleep(random()+1)
        try:
            r = requests.get(url, headers=self.headers, timeout=(3.05, 10))
        except requests.exceptions.ChunkedEncodingError as e:
            LOG.error('获取预售证信息失败! 预售证id:%s', ysznum)
            return
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('http状态:%s, url %s', r.status_code, url)
            raise myException('http状态:%s, url %s' % (r.status_code, url))
        #两个模板
        if 'newlistone' in r.url:
            #模板1
            soup = BeautifulSoup(r.content.decode('gbk', errors='ignore'), 'html.parser') #lxml
            try:
                trs = soup.find(text=re.compile(r'登记编号：?')).find_parent('table').find_all('tr')
            except:pass
            try:
                lr[metadatas[58]]['预售许可证号'] = re.sub(r'\s+', '', trs[2].getText(strip=True))
            except:pass
            try:
                lr[metadatas[58]]['售房单位'] = soup.find('td', text=re.compile(r'售房单位')).find_next('td').getText(strip=True)
            except:pass
            try:
                lr[metadatas[58]]['楼号'] = soup.find('td', text=re.compile(r'楼号')).find_next('td').getText(strip=True)
            except:pass
            try:
                lr[metadatas[58]]['预售套数/间数'] = re.sub(r'\s+', '', soup.find('td', text=re.compile(r'预售套数/间数')).find_next('td').getText(strip=True))
            except:pass
            try:
                lr[metadatas[58]]['售面积 住宅/非住宅'] = re.sub(r'\s+', '', soup.find('td', text=re.compile(r'售面积\s*住宅/非住宅')).find_next('td').getText(strip=True))
            except:pass
            try:
                lr[metadatas[58]]['预售平均售价 住宅/非住宅'] = re.sub(r'\s+', '', soup.find('td', text=re.compile(r'预售平均售价\s*住宅/非住宅')).find_next('td').getText(strip=True))
            except:pass
            try:
                lr[metadatas[58]]['备注'] = soup.find('td', text=re.compile(r'备注')).find_next('td').getText(strip=True)
            except:pass
            try:
                lr[metadatas[58]]['有效期'] = soup.find('td', text=re.compile(r'有效期')).find_next('td').getText(strip=True)
            except:pass
            try:
                lr[metadatas[58]]['发证机关'] = soup.find(text=re.compile(r'发证机关')).split('：')[-1].strip()
            except:pass
        elif 'prelicence_later' in r.url:
            #模板2
            soup = BeautifulSoup(r.content.decode('utf8', errors='ignore'), 'html.parser') #lxml
            for key in ('预售许可证号', '发证日期', '施工单位', '监理单位',
                        '选聘的前期物业服务公司', '物业管理服务等级标准', '物业管理服务收费标准',
                        '前期物业服务合同有效期', '备注'):
                try:
                    lr[metadatas[58]][key] = soup.find('td', text=re.compile(r'%s[:：]?' % key)).find_next('td').getText(strip=True)
                except:pass
            try:
                lr[metadatas[50]] = soup.find('td', text=re.compile(r'开竣工时间[:：]?')).find_next('td').getText(strip=True).split('-')[-1]
            except:pass
            try:
                tr = soup.find('td', text=re.compile(r'企业法人营业执照[:：]?')).find_parent('tr')
                for indx, td in enumerate(tr.find_all('td')):
                    try:
                        if '土地使用' in td.getText(strip=True):
                            lr[metadatas[33]] = tr.find_next('tr').find_all('td')[indx].getText(strip=True)
                        else:
                            lr[metadatas[58]][td.getText(strip=True)] = tr.find_next('tr').find_all('td')[indx].getText(strip=True)
                    except:pass
            except:pass
            try:
                tr = soup.find('td', text=re.compile(r'房\s*屋[:：]?')).find_parent('tr')
                for indx, td in enumerate(tr.find_all('td')[1:]):
                    try:
                        lr[metadatas[58]][td.getText(strip=True)] = tr.find_next('tr').find_all('td')[indx].getText(strip=True)
                    except:pass
            except:pass
        else:
            raise myException('未配置此预售证的解析模板, 预售证链接:%s' % r.url)

    #解析项目列表
    def getitem(self, urlbean):
        LOG.info('郑州网签 %s_%s 信息', urlbean.param[metadatas[6]], urlbean.param[metadatas[8]])
        time.sleep(random()+1)
        r = requests.get(urlbean.url, headers=self.headers, timeout=(3.05, 20))
        if(r.status_code != requests.codes.ok and r.status_code != 404):
            LOG.warning('http状态:%s, url %s', r.status_code, urlbean.url)
            raise myException('http状态:%s, url %s' % (r.status_code, urlbean.url))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        #存储页面信息
        self.htmlwrite.save('%s\\%s\\%s' % (self.__class__.__name__, self.duefname(urlbean.param[metadatas[2]]), self.duefname(urlbean.param[metadatas[6]])), self.duefname(urlbean.param[metadatas[8]]), r.content.decode('gbk'))
        t1 = time.time()
        soup = BeautifulSoup(r.content.decode('gbk', errors='ignore'), 'html.parser') #lxml
        lr = urlbean.param
        #解析数据
        lr[metadatas[59]] = urlbean.order[:-1]+'3'
        #填充为空的字段
        self.completionlr(lr, metadatas)
        #如果是404楼栋信息页面报错就直接存储信息
        if r.status_code == 404:
            lr[metadatas[58]] = json.dumps(lr[metadatas[58]], ensure_ascii=False)
            #存储
            MySqlEx.savewq([lr], metadatas)
            return
        ls = []
        #解析状态对应关系
        smap = {'#FF0000':'限制', '#33CCFF':'已售', '#00CC33':'可售', '#FF00FF':'认购'}
        table_head = []
        indx = 0
        for cell in soup.find('table', id='mytable').find_all('td'):
            #判断出来单元、层、户
            dy = cell.find('div', text=re.compile(r'单元'))
            if dy:
                table_head.append(dy.getText(strip=True))
                print(dy.text)
            else:
                lc = cell.find('div', text=re.compile(r'第.*层'))
                if lc:
                    cr = dict(lr)
                    cr[metadatas[14]] = lc.getText(strip=True)
                    print(lc.text)
                else:
                    h = cell.find('table')
                    if h:
                        dr = copy.deepcopy(cr or lr)
                        #判断与单元有对应关系
                        try:
                            if len(table_head)==len(list(filter(lambda x:x.find('td'), filter(lambda x:x.find('table'), h.find_parent('tr').find_all('td', recursive=False))))):
                                dr[metadatas[11]] = table_head[indx%len(table_head)]
                        except:pass
                        for xcell in h.find_all('td'):
                            hr = copy.deepcopy(dr or cr or lr)
                            hr[metadatas[16]] = hr[metadatas[54]] = xcell.getText(strip=True)
                            try:
                                sp = BeautifulSoup(xcell['info'], 'html.parser')
                                hr[metadatas[39]] = sp.find('td', text='户型：').next_sibling.next_sibling.text
                            except:pass
                            try:
                                hr[metadatas[38]] = sp.find('td', text='用途：').next_sibling.next_sibling.text
                            except:pass
                            #增加在售状态判定
                            try:
                                hr[metadatas[58]]['状态'] = smap(xcell['bgcolor'].strip())
                            except:
                                hr[metadatas[58]]['状态'] = '状态解析异常'
                            hr[metadatas[58]] = json.dumps(dr[metadatas[58]], ensure_ascii=False)
                            ls.append(hr)
                        indx+=1
        t2 = time.time()
        LOG.info('解析页面耗时:%f' % (t2-t1))
        #存储
        MySqlEx.savewq(ls, metadatas)


if __name__ == '__main__':
    zzfdc = wwwzzfdccomcn()
    # for page in zzfdc.default(UrlBase('http://www.zzfdc.gov.cn/spfcs/search.do', 'wwwzzfdccomcn', order='0123456789')):
    #     for project in zzfdc.getpage(page):
    #         for ld in zzfdc.getproject(project)[:2]:
    #             zzfdc.getitem(ld)
    for ld in zzfdc.getproject(UrlBean("http://www.zzfdc.gov.cn/spfcs/showLp.do?showType=Lpdn&LpName=OK&LpId=123", 'wwwfangdicom#getproject', param={metadatas[58]:{}}, headers={'page':20, 'pname':'锦龙居2号楼'}, order='0123456789')):
        zzfdc.getitem(ld)