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
#解析百姓网站
class wwwbxcom(ParserBase):
    htmlwrite = HtmlFile()
    headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36 LBBROWSER', 'Connection': 'keep-alive'}
    shi = re.compile(r'(\d+)室|卧|卧室')
    ting = re.compile(r'(\d+)厅')
    wei = re.compile(r'(\d+)卫')
    chu = re.compile(r'(\d+)厨')
    yangtai = re.compile(r'(\d+)台|阳台')

    t_90 = ('陇南','嘉峪关','阿拉善','鹤岗','塔城','黑河','怒江','绍兴','崇左','德宏','伊春','湖州',
            '普洱','百色','双鸭山','周口','吕梁','齐齐哈尔','梅州','六盘水','牡丹江','绥化','白山',
            '咸宁','乌海','邢台','广元','衡水','云浮','潮州','佳木斯','鹤壁','红河州','丽水','嘉兴',
            '安顺','阳泉','舟山','鄂州','延安','通化','防城港','衡阳','随州','盘锦','承德','鸡西',
            '焦作','邯郸','亳州','金昌','河池','文山','临沧','拉萨','呼伦贝尔','石嘴山','朝阳',
            '张家口','汕尾','台州','贺州','三门峡','安阳','荆门','本溪','北海','黄冈','七台河',
            '抚顺','晋城','邵阳','酒泉','大理','葫芦岛','广安','喀什','娄底','岳阳','阜新','滁州',
            '沧州','衢州','鞍山','晋中','白城','济宁','四平','新余','商丘','长治','郴州','钦州',
            '楚雄','内江','张家界','吴忠','菏泽','孝感','赣州','眉山','十堰','定西','大庆','安庆',
            '咸阳','大同','乐山','蚌埠','宿州','阿克苏','西宁','韶关','清远','保山','武威','铜陵',
            '白银','宝鸡','乌兰察布','聊城','松原','上饶','临沂','镇江','昭通','宁德','东营','黄山',
            '张掖','汕头','莱芜','宣城','恩施','唐山','玉林','九江','西双版纳','阜阳','滨州','漯河',
            '鄂尔多斯','南充','湘潭','通辽','莆田','天水','巴音郭楞','鹰潭','辽源','德阳','日照',
            '淮北','揭阳','怀化','铁岭','开封','昌吉','绵阳','萍乡','连云港')

    def __init__(self):
        super(wwwbxcom, self).__init__()

    def default(self, urlbase):
        LOG.info('默认方法获得城市列表!')
        time.sleep(2.5)
        r = requests.get(urlbase.url, headers=self.headers, timeout=(3.05, 3.5))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwbxcom %s 返回状态:%s', urlbase.url, r.status_code)
            return None
        soup = BeautifulSoup(r.content.decode('utf8', errors='ignore'), 'html.parser') #lxml
        citys = soup.find('ul',attrs={'class':'wrapper'}).find_all('a')
        ls = []
        i_order = urlbase.order+'0'
        for i in citys:
            if i.text in self.t_90:
                i_count = 1
                ls.append(UrlBean(i['href']+'ershoufang/', self.message('getpages'), param=i_count, headers=i.text, order=i_order))
                LOG.info('获得城市%s页面信息%s', i.text, i['href']+'ershoufang/')
                i_count += 1
        return ls

    #解析城市二手房列表页
    def getpages(self, urlbase):
        LOG.info('fanggetpages获得城市%s二手房列表信息', urlbase.url)
        time.sleep(2.5)
        r = requests.get(urlbase.url, headers=self.headers, timeout=(3.05, 3.5))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwbxcom %s 返回状态:%s', urlbase.url, r.status_code)
            return None
        soup = BeautifulSoup(r.content.decode('utf8', errors='ignore'), 'html.parser') #lxml
        items = soup.find('ul', attrs={'style':'border-top: 1px dotted #eee;'}).find_all('a', attrs={'class':'ad-title'})
        host = '/'.join(r.url.split('/')[:3])
        itemIndex = 1
        i_order = urlbase.order+'1'
        ls = []
        for item in items:
            if '/ershoufang/' in item['href']:
                strUrl = item['href'] if 'http' in item['href'].lower() else host+item['href']
                ls.append(UrlBean(strUrl, self.message('getitem'), key=strUrl, param=urlbase.headers, order=i_order))
                LOG.debug('%s第%d页%d项' % (urlbase.headers, urlbase.param, itemIndex))
                itemIndex += 1

        return ls

    #解析详细页面信息
    def getitem(self, urlbase):
        LOG.info('fanggetinfo获得城市%s挂牌详细信息', urlbase.url)
        time.sleep(2.5)
        r = requests.get(urlbase.url, headers=self.headers, timeout=(3.05, 3.5))
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        self.htmlwrite.save('%s\\%s\\%s' %(self.__class__.__name__, '二手房', urlbase.param), r.url, r.text)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwbxcom %s 返回状态:%s', urlbase.url, r.status_code)
            return None
        soup = BeautifulSoup(r.content.decode('utf8', errors='ignore'), 'html.parser') #lxml
        reText = r.text
        lr = {}
        def _split(str_all, str, index):
            try:
                return _strip(str_all).split(str)[index]
            except Exception:
                return ''

        def _strip(str_info):
            return str_info.strip().replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '')

        title_bs = soup.find('div',attrs={'class':'viewad-title'})
        try:
            lr[metadatas[5]] = _strip(title_bs.h1.string)
        except Exception:
            lr[metadatas[5]] = ''
        lr[metadatas[4]] = r.url
        try:
            city = re.findall("city=(.*?)'>",reText,re.S)
            dr = re._compile(r'<[^>]+>',re.S)
            lr[metadatas[1]] = dr.sub('',city[0].strip())
        except:
            lr[metadatas[1]] =''
        try:
            xqmc= re.findall('<label>小区名：</label>(.*?)</span>',reText,re.S)
            dr = re._compile(r'<[^>]+>',re.S)
            lr[metadatas[6]] = dr.sub('',xqmc[0].strip())
        except:
            lr[metadatas[6]] =''
        try:
            jznd= re.findall('<label>建筑年代：</label>(.*?)</label>',reText,re.S)
            dr = re._compile(r'<[^>]+>',re.S)
            lr[metadatas[9]] = dr.sub('',jznd[0].strip()).replace('年','')
        except:
            lr[metadatas[9]] =''
        try:
            lc= re.findall('<label>楼层：</label>(.*?)</label>',reText,re.S)
            lr[metadatas[11]] = dr.sub('',lc[0].strip())
        except:
            lr[metadatas[11]] =''
        try:
            # lc= re.findall('<label>楼层：</label>(.*?)</label>',reText,re.S)
            # dr = re._compile(r'<[^>]+>',re.S)
            dqc = dr.sub('',lc[0].strip()).split('/')
            lr[metadatas[13]]=dqc[0].replace('层','')
        except:
            lr[metadatas[13]] =''
        try:
            # zlc= re.findall('<label>楼层：</label>(.*?)</label>',reText,re.S)
            # dr = re._compile(r'<[^>]+>',re.S)
            zlc1 = dr.sub('',lc[0].strip()).split('/')
            lr[metadatas[12]]=zlc1[1].replace('层','')
        except:
            lr[metadatas[12]] =''
        try:
            cx= re.findall('<label>房间朝向：</label>(.*?)</span>',reText,re.S)
            dr = re._compile(r'<[^>]+>',re.S)
            lr[metadatas[14]] = dr.sub('',cx[0].strip())
        except:
            lr[metadatas[14]] =''
        try:
            jzmj= re.findall('<label>面积：</label>(.*?)</label>',reText,re.S)
            dr = re._compile(r'<[^>]+>',re.S)
            lr[metadatas[15]] = dr.sub('',jzmj[0].strip()).replace('平米','')
        except:
            lr[metadatas[15]] =''
        try:
            hx= re.findall('<label>房型：</label>(.*?)</span>',reText,re.S)
            dr = re._compile(r'<[^>]+>',re.S)
            lr[metadatas[17]] = dr.sub('',hx[0].strip())
        except:
            lr[metadatas[17]] =''
        try:
            lr[metadatas[18]]= re.search(wwwbxcom.shi,lr[metadatas[17]]).group(1)
        except:
            lr[metadatas[18]] =''
        try:
            lr[metadatas[19]]= re.search(wwwbxcom.ting,lr[metadatas[17]]).group(1)
        except:
            lr[metadatas[19]] =''
        try:
            lr[metadatas[20]]= re.search(wwwbxcom.wei,lr[metadatas[17]]).group(1)
        except:
            lr[metadatas[20]] =''
        try:
            zjg= re.findall('<label>价格：</label>(.*?)</span>',reText,re.S)
            dr = re._compile(r'<[^>]+>',re.S)
            lr[metadatas[23]] = dr.sub('',zjg[0].strip()).replace('万元','')
        except:
            lr[metadatas[23]] =''
        print(lr[metadatas[23]])
        try:
            zhuangxiu= re.findall('<label>装修情况：</label>(.*?)</label>',reText,re.S)
            dr = re._compile(r'<[^>]+>',re.S)
            lr[metadatas[29]] = dr.sub('',zhuangxiu[0].strip())
        except:
            lr[metadatas[29]] =''
        try:
            jjr= re.findall('>经纪人(.*?)</a>',reText,re.S)
            dr = re._compile(r'<[^>]+>',re.S)
            lr[metadatas[33]] = dr.sub('',jjr[0].strip())
        except:
            lr[metadatas[33]] =''
        try:
            jjrlj = soup.find('div',attrs={'class':'poster-detail'}).find_all('a',attrs={'class':'poster-name'})
            for a in jjrlj:
                lr[metadatas[34]]=re.findall('href="(.*?)"',str(a),re.S)[0]
        except:
            lr[metadatas[34]] =''
        try:
            jjgs= re.findall('>经纪人(.*?)</p>',reText,re.S)
            dr = re._compile(r'<[^>]+',re.S)
            jjgs1 = dr.sub('',jjgs[0].strip()).split('>>')
            lr[metadatas[35]] =jjgs1[1]
        except:
            lr[metadatas[35]] =''
        try:
            time1= re.findall('>注册时间：(.*?)</div>',reText,re.S)
            dr = re._compile(r'<[^>]+',re.S)
            lr[metadatas[39]] = dr.sub('',time1[0].strip())
        except:
            lr[metadatas[39]] =''
        print(lr[metadatas[39]])
        try:
            photo= re.findall('<label>联系：</label>(.*?)</a>',reText,re.S)
            photo1= re.findall("<a data-contact='(.*?)'",reText,re.S)
            dr = re._compile(r'<[^>]+>',re.S)
            dianhua1 = dr.sub('',photo1[0].strip())
            dianhua2 = dr.sub('',photo[0].strip()).replace('****','')
            lr[metadatas[37]] =dianhua2+dianhua1
        except:
            lr[metadatas[37]] =''
        print(lr[metadatas[37]])

        lr[metadatas[0]] ='s00000bx'
        lr[metadatas[66]] ='bx'

        lr = self.completionlr(lr,metadatas)

        # with open('baixing.txt','a+',encoding='utf8') as f:
        #     f.write('\t'.join([re.sub('r\W|\r|\n', '', item)for item in metadatas]))
        #     f.write('\n')
        # with open('baixing.txt','a+',encoding='utf8') as f:
        #     f.write('\t'.join([re.sub('r\W|\r|\n', '', lr[iitem])for iitem in metadatas]))
        #     f.write('\n')
        #将分析的信息写入数据库
        # self.mysql.save(lr, metadatas)
        MySqlEx.save(lr, metadatas)
    #def getinfo(self, urlbase):
        #LOG.info('fang8getinfo获得%s挂牌详细信息' , urlbase.url)


if __name__ == '__main__':
    wfang = wwwbxcom()
    # print(len(wfang.default(UrlBase('http://www.baixing.com/?changeLocation=yes&return=%2F', 'wwwbxcom',order='123'))))
    # print(len(wfang.getpages(UrlBean('http://nujiang.baixing.com/ershoufang/', 'wwwsfcom#getitem', param=10, headers='哈尔滨',order='123'))))
    wfang.getitem(UrlBean('http://guangyuan.baixing.com/ershoufang/a973566917.html', 'wwwbxcom#getitem', param='北京',order='1234'))
#     ls = ('http://nujiang.baixing.com/ershoufang/a960204291.html',