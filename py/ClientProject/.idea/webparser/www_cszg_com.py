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
#解析城市中国网站
class wwwcszgcom(ParserBase):
    htmlwrite = HtmlFile()
    headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36 LBBROWSER', 'Connection': 'keep-alive'}
    shi = re.compile(r'(\d+)室|卧|卧室')
    ting = re.compile(r'(\d+)厅')
    wei = re.compile(r'(\d+)卫')
    chu = re.compile(r'(\d+)厨')
    yangtai = re.compile(r'(\d+)台|阳台')

    t_90 = ('陇南都市网','嘉峪关在线','阿拉善在线','鹤岗在线','塔城','黑河在线','怒江在线','绍兴在线','崇左在线','德宏在线','伊春信息在线','湖州城市在线',
            '普洱百姓网','百色在线','双鸭山之窗','周口在线','吕梁在线','齐齐哈尔在线','梅州在线','六盘水','牡丹江在线','绥化都市网','白山网',
            '咸宁网','乌海网','邢台在线','广元城市通','衡水在线','云浮在线','潮州','佳木斯在线','鹤壁在线','红河州','丽水之窗','嘉兴之窗',
            '安顺在线','阳泉网','舟山热线','鄂州在线','延安','通化在线','防城港在线','衡阳在线','随州在线','盘锦在线','承德网','鸡西在线',
            '焦作在线','邯郸城市在线','亳州','金昌之窗','河池信息网','文山在线','临沧热线','拉萨在线','呼伦贝尔之窗','石嘴山信息港','朝阳之窗',
            '张家口之窗','汕尾在线','台州在线','贺州在线','三门峡在线','安阳在线','荆门在线','本溪在线','北海在线','黄冈信息网','七台河网',
            '抚顺在线','晋城热线','邵阳县在线','酒泉热线','大理在线','葫芦岛城市在线','广安之窗','喀什在线','娄底城市在线','岳阳在线','阜新在线','滁州',
            '沧州在线','衢州在线','鞍山在线','晋中在线','白城之窗','济宁在线','四平在线','新余在线','商丘在线','长治在线','郴州在线','钦州之窗',
            '楚雄城市在线','内江在线','张家界门户网','吴忠在线','菏泽在线','孝感城市在线','赣州在线','眉山城市在线','十堰楚天网','定西在线','大庆在线','安庆在线',
            '咸阳在线','大同在线','乐山在线','蚌埠在线','宿州在线','阿克苏在线','西宁在线','韶关九九网','清远在线','保山在线','武威在线','铜陵在线',
            '白银在线','宝鸡在线','乌兰察布在线','聊城在线','松原在线','上饶门户网','临沂海江网','镇江网','昭通在线','宁德在线','东营在线','黄山在线',
            '张掖','汕头在线','莱芜在线','宣城在线','恩施','唐山在线','玉林在线','九江在线','西双版纳在线','阜阳城市在线','滨州在线','漯河在线',
            '鄂尔多斯热线','南充城市在线','湘潭城市网','通辽在线','莆田在线','天水城市在线','巴音郭楞','鹰潭热线','辽源在线','德阳之窗','日照之窗',
            '淮北视窗','揭阳在线','怀化在线','铁岭在线','开封在线','昌吉在线','绵阳在线','萍乡在线','连云港在线')

    def __init__(self):
        super(wwwcszgcom, self).__init__()

    def default(self, urlbase):
        LOG.info('默认方法获得城市!')
        r = requests.get(urlbase.url, headers=self.headers, timeout=(3.05, 3.5))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwcszgcom %s 返回状态:%s', urlbase.url, r.status_code)
            return None
        soup = BeautifulSoup(r.content.decode('utf8', errors='ignore'), 'html.parser') #lxml
        citys = soup.find('div',attrs={'class':'webwrap'}).find_all('a',attrs={'class':'more','target':'_blank'},)
        ls = []
        i_order = urlbase.order+'0'
        for i in citys:
            if i.text !='' and i.text !='\n' and 'city-' in i['href']:
                i_count = 1
                ls.append(UrlBean(urlbase.url+i['href'], self.message('defcity'), param=i_count, headers=i.text, order=i_order))
                LOG.info('获得城市%s页面信息%s', i.text, urlbase.url+i['href'])
                i_count += 1
        return ls

    def defcity(self, urlbase):
        LOG.info('默认方法获得城市列表!')
        r = requests.get(urlbase.url, headers=self.headers, timeout=(3.05, 3.5))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwcszgcom %s 返回状态:%s', urlbase.url, r.status_code)
            return None
        soup = BeautifulSoup(r.content.decode('utf8', errors='ignore'), 'html.parser') #lxml
        citys = soup.find('div',attrs={'class':'citybox'}).find_all('a')
        host = '/'.join(r.url.split('/')[:3])+'/'
        ls = []
        i_order = urlbase.order+'0'
        for i in citys:
            if i.text !='' and i.text !='\n' and 'cityinfo-' in i['href']:
                if i.text in self.t_90:
                    i_count = 1
                    ls.append(UrlBean(host+i['href'], self.message('getarea'), param=i_count, headers=i.text, order=i_order))
                    LOG.info('获得城市%s页面信息%s', i.text, host+i['href'])
                    i_count += 1
        return ls

    def getarea(self, urlbase):
        LOG.info('获得二手房链接!')
        r = requests.get(urlbase.url, headers=self.headers, timeout=(3.05, 3.5))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwcszgcom %s 返回状态:%s', urlbase.url, r.status_code)
            return None
        soup = BeautifulSoup(r.content.decode('utf8', errors='ignore'), 'html.parser') #lxml
        citys = soup.find('ul',attrs={'class':'sort_mod'}).find_all('a')
        ls = []
        i_order = urlbase.order+'0'
        for i in citys:
            #if i.text !='' and i.text !='\n' and '/post/fangwu/' in i['href']:
            if '/post/fangwu/' in i['href']:
                i_count = 1
                ls.append(UrlBean(i['href']+'chushou/', self.message('getpages'), param=i_count, headers=i['href'].split('.')[1:2][0], order=i_order))
                LOG.info('获得%s页面信息%s',i['href'].split('.')[1:2][0],i['href']+'chushou/')
                i_count += 1
        return ls


    #解析城市二手房列表页
    def getpages(self, urlbase):
        LOG.info('fanggetpages获得城市%s二手房列表信息', urlbase.url)
        r = requests.get(urlbase.url, headers=self.headers, timeout=(3.05, 3.5))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwcszgcom %s 返回状态:%s', urlbase.url, r.status_code)
            return None
        soup = BeautifulSoup(r.content.decode('gbk', errors='ignore'), 'html.parser') #lxml
        items = soup.find_all('div',attrs={'class':'esfcen'})
        host = '/'.join(r.url.split('/')[:3])
        itemIndex = 1
        i_order = urlbase.order+'1'
        ls = []
        for item in items:
            item = re.findall('href="(.*?)"',str(item),re.S)[0]
            strUrl = item if 'http' in item.lower() else host+item
            ls.append(UrlBean(strUrl, self.message('getitem'), key=strUrl, param=urlbase.headers, order=i_order))
            LOG.debug('%s第%d页%d项' % (urlbase.headers, urlbase.param, itemIndex))
            itemIndex += 1

        return ls

    #解析详细页面信息
    def getitem(self, urlbase):
        LOG.info('fanggetinfo获得城市%s挂牌详细信息', urlbase.url)
        r = requests.get(urlbase.url, headers=self.headers, timeout=(3.05, 3.5))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        self.htmlwrite.save('%s\\%s\\%s' %(self.__class__.__name__, '二手房', urlbase.param), r.url, r.text)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwcszgcom %s 返回状态:%s', urlbase.url, r.status_code)
            return None
        soup = BeautifulSoup(r.content.decode('gbk', errors='ignore'), 'html.parser') #lxml
        reText = r.text.encode('Latin-1', errors='ignore').decode('gbk', errors='ignore')
        host = '/'.join(r.url.split('/')[:3])
        lr = {}
        def _split(str_all, str, index):
            try:
                return _strip(str_all).split(str)[index]
            except Exception:
                return ''

        def _strip(str_info):
            return str_info.strip().replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '')

        title_bs = soup.find('div',attrs={'class':'d_main'})
        try:
            lr[metadatas[5]] = _strip(title_bs.h1.string)
        except Exception:
            lr[metadatas[5]] = ''
        lr[metadatas[4]] = r.url
        try:
            city = soup.find('div',attrs={'class':'fenleiq'}).find_all('a')[0].text
            lr[metadatas[1]] =city.replace('首页','')
        except:
            lr[metadatas[1]] =''
        try:
            xqmc= re.findall('<dt>所在小区：</dt>(.*?)<dt>所在地址：',reText,re.S)
            dr = re._compile(r'<[^>]+>',re.S)
            lr[metadatas[6]] = dr.sub('',xqmc[0].strip()).replace('( 查看该小区详细介绍 )','')
        except:
            lr[metadatas[6]] =''
        try:
            xqlj= re.findall('<dt>所在小区：</dt>(.*?)</dd>',reText,re.S)
            for a in xqlj:
                xqljs =re.findall('href="(.*?)"',str(a),re.S)[0]
                lr[metadatas[7]] =host+xqljs
        except:
            lr[metadatas[7]] =''
        try:
            xzqdz= re.findall('<dt>所在地址：</dt>(.*?)<dt>',reText,re.S)
            dr = re._compile(r'<[^>]+>',re.S)
            xzqdz = dr.sub('',xzqdz[0].strip())
        except:
            xzqdz =''
        try:
            lr[metadatas[2]] = xzqdz.split('-')[0].strip()
            lr[metadatas[8]] = xzqdz.split('-')[1].strip()
        except:
            lr[metadatas[2]] = ''
            lr[metadatas[8]] = ''
        try:
            jznd= re.findall('<dt>建筑年份：</dt>(.*?)</dd>',reText,re.S)
            lr[metadatas[9]] = dr.sub('',jznd[0].strip())
        except:
            lr[metadatas[9]] =''
        try:
            lc= re.findall('<dt>所在楼层：</dt>(.*?)</dd>',reText,re.S)
            lr[metadatas[11]] = dr.sub('',lc[0].strip()).replace('\r\n              ','')
        except:
            lr[metadatas[11]] =''
        try:
            lr[metadatas[13]]=lr[metadatas[11]].split('/')[0].replace('楼','')
        except:
            lr[metadatas[13]] =''
        try:
            lr[metadatas[12]]=lr[metadatas[11]].split('/')[1].replace('层','').replace('共','')
        except:
            lr[metadatas[12]] =''
        try:
            cx= re.findall('<dt>房屋概况：</dt>(.*?)</dd>',reText,re.S)
            dr = re._compile(r'<[^>]+>',re.S)
            lr[metadatas[14]] = dr.sub('',cx[0].strip()).split(' - ')[1].replace('向','').replace('-','')
        except:
            lr[metadatas[14]] =''
        try:
            mj= re.findall('<dt>房屋户型：</dt>(.*?)</dd>',reText,re.S)
            dr = re._compile(r'<[^>]+>',re.S)
            lr[metadatas[15]] = dr.sub('',mj[0].strip()).replace('\r\n              ','').split('- ')[1].replace('㎡','')
        except:
            lr[metadatas[15]] =''
        try:
            hx= re.findall('<dt>房屋户型：</dt>(.*?)</dd>',reText,re.S)
            dr = re._compile(r'<[^>]+>',re.S)
            lr[metadatas[17]] = dr.sub('',hx[0].strip()).replace('\r\n              ','').split('- ')[0].replace(' ','')
        except:
            lr[metadatas[17]] =''
        try:
            lr[metadatas[18]]= re.search(wwwcszgcom.shi,lr[metadatas[17]]).group(1)
        except:
            lr[metadatas[18]] =''
        try:
            lr[metadatas[19]]= re.search(wwwcszgcom.ting,lr[metadatas[17]]).group(1)
        except:
            lr[metadatas[19]] =''
        try:
            lr[metadatas[20]]= re.search(wwwcszgcom.wei,lr[metadatas[17]]).group(1)
        except:
            lr[metadatas[20]] =''
        try:
            zjg= re.findall('<dt>价　　格：</dt>(.*?)</b>',reText,re.S)
            dr = re._compile(r'<[^>]+>',re.S)
            lr[metadatas[23]] = dr.sub('',zjg[0].strip())
        except:
            lr[metadatas[23]] =''
        try:
            dj= re.findall('</b>(.*?)</dd>',reText,re.S)
            dr = re._compile(r'<[^>]+>',re.S)
            lr[metadatas[24]] = dr.sub('',dj[0].strip()).replace('\r\n              ','').replace('万元(','').replace('元/㎡)','').replace('&nbsp;','').replace('免税房','')
        except:
            lr[metadatas[24]] =''
        try:
            zx= re.findall('<dt>房屋概况：</dt>(.*?)</dd>',reText,re.S)
            dr = re._compile(r'<[^>]+>',re.S)
            lr[metadatas[29]] = dr.sub('',zx[0].strip()).split(' - ')[0]
        except:
            lr[metadatas[29]] =''
        try:
            lxr= re.findall('<dt>联 系 人：</dt>(.*?)<i>',reText,re.S)
            dr = re._compile(r'<[^>]+>',re.S)
            lr[metadatas[33]] = dr.sub('',lxr[0].strip()).replace('：','').replace('--','')
        except:
            lr[metadatas[33]] =''
        try:
            time= re.findall('发布时间：(.*?)信息关注度',reText,re.S)
            dr = re._compile(r'<[^>]+',re.S)
            lr[metadatas[41]] = dr.sub('',time[0].strip()).split()[0]
        except:
            lr[metadatas[41]] =''
        try:
            photo= re.findall('<dt>联系电话：</dt>(.*?)</i>',reText,re.S)
            dr = re._compile(r'<[^>]+>',re.S)
            lr[metadatas[37]] = dr.sub('',photo[0].strip())
        except:
            lr[metadatas[37]] =''
        #print(lr[metadatas[37]])

        lr[metadatas[0]] ='s00000zg'
        lr[metadatas[66]] ='cszg'

        lr = self.completionlr(lr,metadatas)

        MySqlEx.save(lr, metadatas)
    #def getinfo(self, urlbase):
        #LOG.info('fang8getinfo获得%s挂牌详细信息' , urlbase.url)


if __name__ == '__main__':
    wfang = wwwcszgcom()
    # print(len(wfang.default(UrlBase('http://www.ccoo.cn/', 'wwwcszgcom',order='123'))))
    # print(len(wfang.defcity(UrlBase('http://www.ccoo.cn/city-a.html', 'wwwcszgcom',order='123'))))
    # print(len(wfang.getarea(UrlBase('http://www.ccoo.cn/cityinfo-823.html', 'wwwcszgcom',order='123'))))
    # print(len(wfang.getpages(UrlBean('http://www.anxinol.cn/post/fangwu/chushou/', 'wwwcszgcom#getitem', param=10, headers='哈尔滨',order='123'))))
    wfang.getitem(UrlBean('http://www.0937.cc/post/fangwu/chushou/3116970x.html', 'wwwcszgcom#getitem', param='北京',order='1234'))
    wfang.getitem(UrlBean('http://www.0994.ccoo.cn/post/fangwu/chushou/2758061x.html', 'wwwcszgcom#getitem', param='北京',order='1234'))