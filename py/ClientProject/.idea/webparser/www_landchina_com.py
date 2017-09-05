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
# metadatas = ('题名','来源链接','小区名称','所属区域','小区链接','楼栋名称','地址','建成年份',                            #7
#             '总楼层','当前层','朝向','建筑面积','使用面积','产权性质','装修情况','户型','卧室数量',                      #16
#             '客厅数量','卫生间数量','厨房数量','阳台数量','单价','总价','挂牌时间','房屋图片','信息来源',                #25
#             '联系人','经纪公司','电话号码','纬度','经度','发布时间','住宅类别','建筑类别','配套设施','交通状况',         #35
#             '楼盘物业类型','楼盘绿化率','楼盘物业费','数据来源','城市','行政区','str_order')                            #42

metadatas = ('信息来源','城市','行政区','片区','来源链接','题名','小区名称','小区链接','地址','建成年份','房龄',                     #10
             '楼层','总楼层','当前层','朝向','建筑面积','使用面积','户型','卧室数量','客厅数量','卫生间数量',                        #20
             '厨房数量','阳台数量','总价','单价','本月均价','小区开盘单价','住宅类别','产权性质','装修情况','建筑类别',               #30
             '楼盘物业类型','小区简介','联系人','联系人链接','经纪公司','门店','电话号码','服务商圈','注册时间','经纪公司房源编号',    #40
             '发布时间','小区总户数','小区总建筑面积','容积率','小区总停车位','开发商','交通状况','配套设施','楼盘绿化率','物业公司',  #50
             '楼盘物业费','土地使用年限','入住率','学校','地上层数','花园面积','地下室面积','车库数量','车位数量','厅结构',           #60
             '导航','房屋图片','纬度','经度','str_order','数据来源')                                                                          #65

import requests, re
from bs4 import BeautifulSoup, Tag
#解析中国土地市场网站
class wwwlandchinacom(ParserBase):
    headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36 LBBROWSER', 'Connection': 'keep-alive'}
    htmlwrite = HtmlFile()
    lou = re.compile(r'(\d+)\D+(\d+)')
    shi = re.compile(r'(\d+)室|卧|卧室')
    ting = re.compile(r'(\d+)厅')
    wei = re.compile(r'(\d+)卫')
    chu = re.compile(r'(\d+)厨')
    yangtai = re.compile(r'(\d+)台|阳台')
    mi = re.compile(r'(\d+.?\d*)㎡')
    jg = re.compile(r'(\d+.?\d*)[.\W]*万[.\W]*(\d+.?\d*)元/㎡')

    def __init__(self):
        super(wwwlandchinacom, self).__init__()

    def default(self, urlbase):
        LOG.info('生成页面列表!')
        try:
            page = re.search('&page=(-?\d*)', urlbase.url).group(1)
        except:
            page = -1
        finally:
            urlbase.url = re.sub('&page=(-?\d*)', '', urlbase.url)
        r = requests.get(urlbase.url, headers=self.headers, timeout=(30, 60))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwlandchinacom %s 返回状态:%s', urlbase.url, r.status_code)
            raise Exception("status_code:%s" % r.status_code)
        #解析生成页码链接
        #指定抓取多少页
        soup = BeautifulSoup(r.content.decode('gbk', errors='ignore'), 'html.parser') #lxml
        pager = soup.find('td', class_="pager")
        if pager:
            list = []
            i_order = urlbase.order+'0'
            maxpage = re.search('共(\d*)页', pager.text).group(1)
            maxpage = '0' if maxpage =='' else maxpage
            for p in range( int(maxpage) if page=='-1' else min(int(page), int(maxpage))):
                list.append(UrlBean(urlbase.url, self.message('getpages'), param=p+1, order=i_order))
            LOG.info('生成土地市场网共%s页链接!', int(maxpage) if page=='-1' else min(int(page), int(maxpage)))
        else:
            raise Exception("没有找到分页信息,无法判断抓取页数!")
        return list

    #解析城市二手房列表页
    def getpages(self, urlbase):
        LOG.info('wwwlandchinacom获得城市%s二手房列表信息', urlbase.url)
        r = requests.post(urlbase.url, headers=self.headers, data={
            '__EVENTVALIDATION':'/wEWAgLPvNjOBwLN3cj/BBXBEiU8Jnn7400dluym//XklDcNFSxpDoOxTyrn6nBx',
            '__VIEWSTATE':'/wEPDwUJNjkzNzgyNTU4D2QWAmYPZBYIZg9kFgICAQ9kFgJmDxYCHgdWaXNpYmxlaGQCAQ9kFgICAQ8WAh4Fc3R5bGUFIEJBQ0tHUk9VTkQtQ09MT1I6I2YzZjVmNztDT0xPUjo7ZAICD2QWAgIBD2QWAmYPZBYCZg9kFgJmD2QWBGYPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmDxYEHwEFIENPTE9SOiNEM0QzRDM7QkFDS0dST1VORC1DT0xPUjo7HwBoFgJmD2QWAgIBD2QWAmYPDxYCHgRUZXh0ZWRkAgEPZBYCZg9kFgJmD2QWAmYPZBYEZg9kFgJmDxYEHwEFhwFDT0xPUjojRDNEM0QzO0JBQ0tHUk9VTkQtQ09MT1I6O0JBQ0tHUk9VTkQtSU1BR0U6dXJsKGh0dHA6Ly93d3cubGFuZGNoaW5hLmNvbS9Vc2VyL2RlZmF1bHQvVXBsb2FkL3N5c0ZyYW1lSW1nL3hfdGRzY3dfc3lfamhnZ18wMDAuZ2lmKTseBmhlaWdodAUBMxYCZg9kFgICAQ9kFgJmDw8WAh8CZWRkAgIPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmD2QWAmYPZBYEZg9kFgJmDxYEHwEFIENPTE9SOiNEM0QzRDM7QkFDS0dST1VORC1DT0xPUjo7HwBoFgJmD2QWAgIBD2QWAmYPDxYCHwJlZGQCAg9kFgJmD2QWBGYPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmD2QWAmYPFgQfAQUgQ09MT1I6I0QzRDNEMztCQUNLR1JPVU5ELUNPTE9SOjsfAGgWAmYPZBYCAgEPZBYCZg8PFgIfAmVkZAICD2QWBGYPZBYCZg9kFgJmD2QWAmYPZBYCAgEPZBYCZg8WBB8BBYYBQ09MT1I6I0QzRDNEMztCQUNLR1JPVU5ELUNPTE9SOjtCQUNLR1JPVU5ELUlNQUdFOnVybChodHRwOi8vd3d3LmxhbmRjaGluYS5jb20vVXNlci9kZWZhdWx0L1VwbG9hZC9zeXNGcmFtZUltZy94X3Rkc2N3X3p5X2pnZ2dfMDEuZ2lmKTsfAwUCNDYWAmYPZBYCAgEPZBYCZg8PFgIfAmVkZAIBD2QWAmYPZBYCZg9kFgJmD2QWAgIBD2QWAmYPFgQfAQUgQ09MT1I6I0QzRDNEMztCQUNLR1JPVU5ELUNPTE9SOjsfAGgWAmYPZBYCAgEPZBYCZg8PFgIfAmVkZAIDD2QWAgIDDxYEHglpbm5lcmh0bWwFtwY8cCBhbGlnbj0iY2VudGVyIj48c3BhbiBzdHlsZT0iZm9udC1zaXplOiB4LXNtYWxsIj4mbmJzcDs8YnIgLz4NCiZuYnNwOzxhIHRhcmdldD0iX3NlbGYiIGhyZWY9Imh0dHA6Ly93d3cubGFuZGNoaW5hLmNvbS8iPjxpbWcgYm9yZGVyPSIwIiBhbHQ9IiIgd2lkdGg9IjI2MCIgaGVpZ2h0PSI2MSIgc3JjPSIvVXNlci9kZWZhdWx0L1VwbG9hZC9mY2svaW1hZ2UvdGRzY3dfbG9nZS5wbmciIC8+PC9hPiZuYnNwOzxiciAvPg0KJm5ic3A7PHNwYW4gc3R5bGU9ImNvbG9yOiAjZmZmZmZmIj5Db3B5cmlnaHQgMjAwOC0yMDE0IERSQ25ldC4gQWxsIFJpZ2h0cyBSZXNlcnZlZCZuYnNwOyZuYnNwOyZuYnNwOyA8c2NyaXB0IHR5cGU9InRleHQvamF2YXNjcmlwdCI+DQp2YXIgX2JkaG1Qcm90b2NvbCA9ICgoImh0dHBzOiIgPT0gZG9jdW1lbnQubG9jYXRpb24ucHJvdG9jb2wpID8gIiBodHRwczovLyIgOiAiIGh0dHA6Ly8iKTsNCmRvY3VtZW50LndyaXRlKHVuZXNjYXBlKCIlM0NzY3JpcHQgc3JjPSciICsgX2JkaG1Qcm90b2NvbCArICJobS5iYWlkdS5jb20vaC5qcyUzRjgzODUzODU5YzcyNDdjNWIwM2I1Mjc4OTQ2MjJkM2ZhJyB0eXBlPSd0ZXh0L2phdmFzY3JpcHQnJTNFJTNDL3NjcmlwdCUzRSIpKTsNCjwvc2NyaXB0PiZuYnNwOzxiciAvPg0K54mI5p2D5omA5pyJJm5ic3A7IOS4reWbveWcn+WcsOW4guWcuue9kTxiciAvPg0K5aSH5qGI5Y+3OiDkuqxJQ1DlpIcwOTA3NDk5MuWPtyDkuqzlhaznvZHlronlpIcxMTAxMDIwMDA2NjYoMikmbmJzcDs8YnIgLz4NCjwvc3Bhbj4mbmJzcDsmbmJzcDsmbmJzcDs8YnIgLz4NCiZuYnNwOzwvc3Bhbj48L3A+HwEFZEJBQ0tHUk9VTkQtSU1BR0U6dXJsKGh0dHA6Ly93d3cubGFuZGNoaW5hLmNvbS9Vc2VyL2RlZmF1bHQvVXBsb2FkL3N5c0ZyYW1lSW1nL3hfdGRzY3cyMDEzX3l3XzEuanBnKTtkZHHKGVL5wJXB94IHp17BVvO7EcHpac9tJ1q/mGeNaKU/',
            'hidComName':'default',
            'TAB_QuerySortItemList':'282:False',
            'TAB_QuerySubmitConditionData':'',
            'TAB_QuerySubmitOrderData':'282:False',
            'TAB_QuerySubmitPagerData':urlbase.param,
            'TAB_QuerySubmitSortData':'',
            'TAB_RowButtonActionControl':''}, timeout=(30, 60))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwlandchinacom %s 返回状态:%s', urlbase.url, r.status_code)
            raise Exception("status_code:%s" % r.status_code)
        soup = BeautifulSoup(r.content.decode('gbk', errors='ignore'), 'html.parser') #lxml
        table = soup.find('table', id='TAB_contentTable')
        if table is None:
            raise Exception("没有找到table id:%s" % TAB_contentTable)
        list = []
        itemIndex = 1
        i_order = urlbase.order+'1'
        print(r.content.decode('gbk', errors='ignore'))
        for idx, item in enumerate(table.find_all("a")):
            print(idx, item.parent.parent.find('td', class_='gridTdNumber').text, item['href'])
            # if '.shtml' in item['href']:
            #     sUrl = item['href'].split('?')[0]
            #     list.append(UrlBean(sUrl, self.message('getitem'), key=sUrl, param=urlbase.headers, order=i_order))
            #     LOG.debug('%s第%d页%d项' % (urlbase.headers, urlbase.param, itemIndex))
            #     itemIndex += 1
        return list

    #解析详细页面信息
    def getitem(self, urlbase):
        LOG.info('58getinfo获得城市%s挂牌详细信息', urlbase.url)
        t1 = time.time()
        r = requests.get(urlbase.url, headers=self.headers, timeout=(3.05, 1.5))
        t2 = time.time()
        LOG.info('处理58请求getitem耗时:%f' % (t2-t1))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        #存储页面信息
        t1 = time.time()
        self.htmlwrite.save('%s\\%s\\%s' %(self.__class__.__name__, '二手房', urlbase.param), r.url, r.text)
        t2 = time.time()
        if(r.status_code != requests.codes.ok):
            LOG.warning('www58com %s 返回状态:%s', r.request.url, r.status_code)
            return
        t1 = time.time()
        reText = r.text
        soup = BeautifulSoup(r.content.decode('utf8'), 'html.parser') #lxml
        mainPart = soup.find('div', class_='mainTitle')
        lr = {}
        try:
            #获得标题
            #print(metadatas[0], mainPart.div.text)
            lr[metadatas[5]] = mainPart.div.text
        except Exception as e:
            lr[metadatas[5]] = ''

        try:
            #获得来源链接
            #print(metadatas[1], r.url)
            lr[metadatas[4]] = r.url
        except Exception as e:
            lr[metadatas[4]] = ''

        infoPart = soup.find('div', class_='sumary')
        try:
            weizhi = soup.find('div', class_='su_tit', text='位置：').parent
            pos = re.sub(r'[\W\r\n]+', '-', weizhi.getText(strip=True)).split('-')
            #获得小区名称
            #print(metadatas[2], pos[3])
            lr[metadatas[6]] = pos[3]
        except Exception as e:
            lr[metadatas[6]] = ''

        try:
            #获得所属区域
            #print(metadatas[3], pos[2])
            lr[metadatas[3]] = pos[2]
        except Exception as e:
            lr[metadatas[3]] = ''

        try:
            #获得小区链接
            #print(metadatas[4], weizhi.find_all('a')[2]['href'])
            lr[metadatas[7]] = weizhi.find_all('a')[2]['href']
        except Exception as e:
            lr[metadatas[7]] = ''


        xq = soup.find('div', class_='xiaoqu_txt')
        try:
            #获得地址
            #print(metadatas[6], xq.find_all('p')[1].text.split("：")[1])
            lr[metadatas[8]] = xq.find_all('p')[1].text.split("：")[1]
        except Exception as e:
            lr[metadatas[8]] = ''

        fydes = soup.find('section', id='fyms')
        try:
            #建成年份
            li = fydes.find(lambda x:re.compile('建造年代：').match(x.text) is not None)
            result = ''
            for li in li.next_siblings:
                if isinstance(li, Tag) and li.name == 'li':
                    result = li.text
                    break
            #print(metadatas[7], result)
            lr[metadatas[9]] = result
        except Exception as e:
            lr[metadatas[9]] = ''

        try:
            #总楼层
            li = fydes.find(lambda x:re.compile('房屋楼层：').match(x.text) is not None)
            result = ''
            for li in li.next_siblings:
                if isinstance(li, Tag) and li.name == 'li':
                    result = li.text
                    break
            lr[metadatas[11]] = result
            gr = re.search(www58com.lou, result).groups()
            #print(metadatas[8], gr[1])
            lr[metadatas[12]] = gr[1]
        except Exception as e:
            lr[metadatas[11]] = ''
            lr[metadatas[12]] = ''

        try:
            #当前层
            #print(metadatas[9], gr[0])
            lr[metadatas[13]] = gr[0]
        except Exception as e:
            lr[metadatas[13]] = ''

        try:
            #朝向
            li = fydes.find(lambda x:re.compile('朝向：').match(x.text) is not None)
            result = ''
            for li in li.next_siblings:
                if isinstance(li, Tag) and li.name == 'li':
                    result = li.text
                    break
            #print(metadatas[10], result)
            lr[metadatas[14]] = result
        except Exception as e:
            lr[metadatas[14]] = ''

        try:
            #建筑面积
            hx = soup.find('div', class_='su_tit', text='户型：').parent
            #print(metadatas[11], re.search(www58com.mi, hx.text).group(1))
            lr[metadatas[15]] = re.search(www58com.mi, hx.text).group(1)
        except Exception as e:
            lr[metadatas[15]] = ''

        try:
            #使用面积
            symj = re.findall('（套内(.*?)㎡）',hx.text,re.S)[0]
            lr[metadatas[16]] = symj
        except Exception as e:
            lr[metadatas[16]] = ''

        try:
            #产权性质
            li = fydes.find(lambda x:re.compile('房屋类型：').match(x.text) is not None)
            result = ''
            for li in li.next_siblings:
                if isinstance(li, Tag) and li.name == 'li':
                    result = li.text
                    break
            #print(metadatas[13], result)
            lr[metadatas[28]] = result
        except Exception as e:
            lr[metadatas[28]] = ''

        try:
            #装修情况
            li = fydes.find(lambda x:re.compile('装修程度：').match(x.text) is not None)
            result = ''
            for li in li.next_siblings:
                if isinstance(li, Tag) and li.name == 'li':
                    result = li.text
                    break
            #print(metadatas[14], result)
            lr[metadatas[29]] = result.replace('找装修','').strip()
        except Exception as e:
            lr[metadatas[29]] = ''

        try:
            #户型
            #print(metadatas[15], ''.join(re.sub(r'[\W|\r|\n]+', '-', hx.getText(strip=True)).split('-')[1:4]))
            lr[metadatas[17]] = ''.join(re.sub(r'[\W\r\n]+', '-', hx.getText(strip=True)).split('-')[1:4])
        except Exception as e:
            lr[metadatas[17]] = ''

        try:
            #卧室数量
            #print(metadatas[16], re.search(www58com.shi, hx.text).group(1))
            lr[metadatas[18]] = re.search(www58com.shi, hx.text).group(1)
        except Exception as e:
            lr[metadatas[18]] = ''

        try:
            #客厅数量
            #print(metadatas[17], re.search(www58com.ting, hx.text).group(1))
            lr[metadatas[19]] = re.search(www58com.ting, hx.text).group(1)
        except Exception as e:
            lr[metadatas[19]] = ''

        try:
            #卫生间数量
            #print(metadatas[18], re.search(www58com.wei, hx.text).group(1))
            lr[metadatas[20]] = re.search(www58com.wei, hx.text).group(1)
        except Exception as e:
            lr[metadatas[20]] = ''

        try:
            #厨房数量
            #print(metadatas[19], re.search(www58com.chu, hx.text).group(1))
            lr[metadatas[21]] = re.search(www58com.chu, hx.text).group(1)
        except Exception as e:
            lr[metadatas[21]] = ''

        try:
            #阳台数量
            #print(metadatas[20], re.search(www58com.yangtai, hx.text).group(1))
            lr[metadatas[22]] = re.search(www58com.yangtai, hx.text).group(1)
        except Exception as e:
            lr[metadatas[22]] = ''

        try:
            #单价
            sj = infoPart.find(lambda x:re.compile('售价：').match(x.text) is not None)
            jg = re.search(www58com.jg, sj.parent.text)
            #print(metadatas[21], jg.group(2))
            lr[metadatas[24]] = jg.group(2)
        except Exception as e:
            lr[metadatas[24]] = ''

        try:
            #总价
            #print(metadatas[22], jg.group(1))
            lr[metadatas[23]] = jg.group(1)
        except Exception as e:
            lr[metadatas[23]] = ''

        # try:
        #     #挂牌时间,动态JS
        #     #print(metadatas[23], mainPart.find('li', class_='time').script)
        #     #for child in mainPart.find('li', class_='time').children:
        #         #print(child)
        #     lr[metadatas[23]] = mainPart.find('li', class_='time').text
        # except Exception as e:
        #     lr[metadatas[23]] = ''

        try:
            #房屋图片
            #print(metadatas[24], soup.find('img', id='img1')['src'])
            lr[metadatas[62]] = soup.find('img', id='img1')['src']
        except Exception as e:
            lr[metadatas[62]] = ''

        #信息来源
        # try:
        #     lr[metadatas[25]] = soup.find('div', class_='nav').a.text
        # except Exception as e:
        #     lr[metadatas[25]] = ''

        try:
            #联系人
            #print(metadatas[26], fydes.find('p', class_='broker_r_p').text)
            lr[metadatas[33]] = fydes.find('p', class_='broker_r_p').text.split('该经纪人')[0].strip()
        except Exception as e:
            lr[metadatas[33]] = ''

        try:
            #联系人链接
            #print(metadatas[26], fydes.find('p', class_='broker_r_p').text)
            lr[metadatas[34]] = fydes.find('p', class_='broker_r_p').find('a')['href'].strip()
        except Exception as e:
            lr[metadatas[34]] = ''

        # try:
        #     #经纪公司
        #     # jjr = soup.find('div', class_='jjreninfo')
        #     # if (jjr):
        #     #     lr[metadatas[35]] = jjr.find('li', class_='jjreninfo_des_com').text.split('官方认证')[0].strip()
        #     # else:
        #     lr[metadatas[35]] = re.findall('"I":10276,"V":"(.*?)"',reText,re.S)[0]
        # except Exception as e:
        #     lr[metadatas[35]] = ''

        if lr[metadatas[34]] != '' and 'my.58' not in lr[metadatas[34]]:
            try:
                rjjr = requests.get(lr[metadatas[34]], headers=self.headers, timeout=(3.05, 2.5))
                reTextjjr = rjjr.text
            except:
                reTextjjr = ''
            try:
                rejjgs = re.findall('<dt>所属公司：</dt>(.*?)</dd>',reTextjjr,re.S)[0]
                dr = re.compile(r'<[^>]+>',re.S)
                lr[metadatas[35]] =  re.sub(dr,'',rejjgs).strip()
            except:
                lr[metadatas[35]] = ''
            try:
                rejjmd = re.findall('<dt>所属门店：</dt>(.*?)</dd>',reTextjjr,re.S)[0]
                dr = re.compile(r'<[^>]+>',re.S)
                lr[metadatas[36]] =  re.sub(dr,'',rejjmd).strip()
            except:
                lr[metadatas[36]] = ''
            try:
                lr[metadatas[38]] = re.findall('<li><label>服务区域：</label><span>(.*?)</span>',reTextjjr,re.S)[0]
            except:
                lr[metadatas[38]] = ''
        else:
            try:
            #经纪公司
                lr[metadatas[35]] = re.findall('"I":10276,"V":"(.*?)"',reText,re.S)[0]
            except Exception as e:
                lr[metadatas[35]] = ''
            lr[metadatas[36]] = lr[metadatas[38]] =''


        try:
            #电话号码
            lr[metadatas[37]] = fydes.find('span', class_='arial').text.strip()
        except Exception as e:
            lr[metadatas[37]] = ''

        lr[metadatas[41]] = datetime.datetime.now().strftime('%Y-%m-%d')

        try:
            des_table = fydes.find('ul', class_='des_table')
            #住宅类别
            li = des_table.find(lambda x:re.compile('住宅类别：').match(x.text) is not None)
            result = ''
            for li in li.next_siblings:
                if isinstance(li, Tag) and li.name == 'li':
                    result = li.text
                    break
            #print(metadatas[32], result)
            lr[metadatas[27]] = result
        except Exception as e:
            lr[metadatas[27]] = ''

        try:
            #建筑类别
            li = des_table.find(lambda x:re.compile('建筑结构：').match(x.text) is not None)
            result = ''
            for li in li.next_siblings:
                if isinstance(li, Tag) and li.name == 'li':
                    result = li.text
                    break
            lr[metadatas[30]] = result
        except Exception as e:
            lr[metadatas[30]] = ''

        try:
            #配套设施,动态JS
            spans = fydes.find('div', class_='peizhi').find_all('span')
            #print(metadatas[34], ''.join(span.text for span in spans))
            ptstr = ''.join(span.text for span in spans)
            lr[metadatas[48]] = re.search("var tmp = '(.*?)';",ptstr,re.S).group(1)
        except Exception as e:
            lr[metadatas[48]] = ''

        try:
            #交通状况
            ps = fydes.find('article', class_='description_con').find_all('p')
            #print(metadatas[35], ''.join(p.text for p in ps))
            strjt = ''.join(p.text for p in ps)
            lr[metadatas[47]] = strjt[0:2000]
        except Exception as e:
            lr[metadatas[47]] = ''

        try:
            #土地使用年限
            li = des_table.find(lambda x:re.compile('产权：').match(x.text) is not None)
            result = ''
            for li in li.next_siblings:
                if isinstance(li, Tag) and li.name == 'li':
                    result = li.text
                    break
            lr[metadatas[52]] = result
        except Exception as e:
            lr[metadatas[52]] = ''

        lr[metadatas[10]] = ''
        lr[metadatas[25]] = ''
        lr[metadatas[26]] = ''
        lr[metadatas[31]] = ''
        lr[metadatas[32]] = ''
        lr[metadatas[39]] = ''
        lr[metadatas[40]] = ''
        lr[metadatas[42]] = ''
        lr[metadatas[43]] = ''
        lr[metadatas[44]] = ''
        lr[metadatas[45]] = ''
        lr[metadatas[46]] = ''
        lr[metadatas[49]] = ''
        lr[metadatas[50]] = ''
        lr[metadatas[51]] = ''
        lr[metadatas[53]] = ''
        lr[metadatas[54]] = ''
        lr[metadatas[55]] = ''
        lr[metadatas[56]] = ''
        lr[metadatas[57]] = ''
        lr[metadatas[58]] = ''
        lr[metadatas[59]] = ''
        lr[metadatas[60]] = ''
        lr[metadatas[63]] = ''
        lr[metadatas[64]] = ''


        lr[metadatas[0]] = 's0000058'
        lr[metadatas[66]] = '58'

        try:
            #导航
            lr[metadatas[61]] = ">".join([dd.text.strip().replace('二手房','') for dd in soup.find('div', class_='nav').find_all('a')])
        except Exception as e:
            lr[metadatas[61]] = ''

        try:
            #城市
            #print(metadatas[40], soup.find('div', class_='nav').a.text.split('58')[0])
            lr[metadatas[1]] = soup.find('div', class_='nav').a.text.split('58')[0]
        except Exception as e:
            lr[metadatas[1]] = ''

        try:
            #行政区
            #print(metadatas[41], pos[1])
            lr[metadatas[2]] = pos[1]
        except Exception as e:
            lr[metadatas[2]] = ''
        lr[metadatas[65]] = urlbase.order if urlbase.order is not None else ''
        t2 = time.time()
        LOG.info('解析页面耗时:%f' % (t2-t1))
        #将分析的信息写入数据库
        #www58com.mysql.save(lr, metadatas)
        MySqlEx.save(lr, metadatas)

    #def getinfo(self, urlbase):
        #LOG.info('58getinfo获得%s挂牌详细信息' , urlbase.url)


if __name__ == '__main__':
    #http://www.landchina.com/default.aspx?tabid=263&ComName=default, 公告信息地址
    wlc = wwwlandchinacom()
    print(len(wlc.default(UrlBase('http://www.landchina.com/default.aspx?tabid=263&ComName=default&page=-1', 'wwwlandchinacom', order='12345632156'))))
    #print(wlc.getpages(UrlBean('http://www.landchina.com/default.aspx?tabid=263&ComName=default', 'wwwlandchinacom#getitem', param=200, order='12345632156')))
    print(wlc.getpages(UrlBean('http://www.landchina.com/default.aspx?tabid=263&ComName=default', 'wwwlandchinacom#getitem', param=310, order='12345632156')))
    #print(w58.getpages(UrlBean('http://bj.58.com/ershoufang/pn2', 'www58com#getitem', param=9, headers='北京')))
    #print(w58.getitem(UrlBean('http://deyang.58.com/ershoufang/25038273012807x.shtml', 'www58com#getpages', param='北京',order='12345632156')))
#print(www58com.__name__)
#print(www58com.getcitys.__name__)
#print(isinstance([], list))

