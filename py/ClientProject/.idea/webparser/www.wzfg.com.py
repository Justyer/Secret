#温州房地产信息网
import sys, os
import requests, re, urllib.parse
from urllib.parse import urlencode
from bs4 import BeautifulSoup, Tag, NavigableString
from selenium.webdriver.common.by import By
import copy

if __name__ == '__main__':
    parent_path = os.path.dirname(os.getcwd()) #获取当前工作目录，也就是在哪个目录下运行这个程序
    sys.path.append(parent_path)

from Common.BaseClass import  *
from Common.OutTxt import *
from Common.OutHtml import *
from webparser.webparserbase import ParserBase
LOG=logging.getLogger()
LOG.handlers[0].setLevel(logging.INFO)
LOG.handlers[1].setLevel(logging.INFO)
#driver = webdriver.Firefox()

#解析温州网签数据
class wwwwzfgcom(ParserBase,BaseClass):
    def __init__(self):
        super(wwwwzfgcom, self).__init__()

    SaveDir =parent_path + "\\OutFile\\温州房地产信息网\\"
    #解析解析温州网签列表
    def GetPageList(self, url,maxPage):
        pages = maxPage
        ls = []
        for page in range(int(pages)):
            strUrl = url +"?currPage=" + str(page)
            ls.append(strUrl)
        return ls

    #解析列表分页信息
    def getProjectUrl(self, urllist):
        ls = []
        for url in urllist:
            LOG.info('温州网签 第%s页', url)
            #time.sleep(random()+1)
            try:
                r = requests.get(url, headers=self.headers, timeout=(3.05, 10))
                LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
                if(r.status_code != requests.codes.ok):
                    LOG.warning('http状态:%s, url %s', r.status_code, urlbean.url)
                    outTxtLine(File_Operation_Type.a.name,parent_path + "\\OutFile\\","温州网签Error.txt",url + "\t"+r.status_code)
                    #raise myException('http状态:%s, url %s' % (r.status_code, urlbean.url))
                ListReg = re.compile('onclick=\"window.open\(\'(?P<url>.*?)\'\)\"')
                webCon = r.content.decode('gbk', errors='ignore')
                #解析列表
                ListInfo = ListReg.findall(webCon)
               #去掉表头和表尾
                for info  in ListInfo:
                    strUrl ="http://www.wzfg.com/realweb/stat/" + info
                    ls.append(strUrl)
            except:
                outTxtLine(File_Operation_Type.a.name,parent_path + "\\OutFile\\","温州网签Error.txt",url + "\t访问超时")
        for s in ls:
            outTxtLine(File_Operation_Type.a.name,parent_path + "\\OutFile\\","楼盘Url.txt",s)
        return ls


    #解析项目
    def getproject(self, urlbean):
        LOG.info('温州网签 第%s页 %s', urlbean.headers['page'], urlbean.headers['pname'])
        #time.sleep(random()+1)

        try:
            r = requests.post(urlbean.url, headers=self.headers, timeout=(3.05, 10))
        except:
            outTxtLine(File_Operation_Type.a.name,parent_path + "\\OutFile\\","温州网签Error.txt",url + "\t访问超时")
            return
        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('http状态:%s, url %s', r.status_code, urlbean.url)
            outTxtLine(File_Operation_Type.a.name,parent_path + "\\OutFile\\","温州网签Error.txt", urlbean.url + "\t"+r.status_code)
        webCon = r.content.decode('gbk', errors='ignore')
        soup = BeautifulSoup(webCon, 'html.parser') #lxml
        #soup = BeautifulSoup(login_form) #lxml
        #解析项目列表
        ls = []
        i_order = urlbean.order[:-1]+'2'
        #初始化抓取信息
        lr = {metadatas[58]:{}}
        lr[metadatas[Animal.Sheng]] = '浙江'
        lr[metadatas[Animal.Chengshi]] = '温州'
        lr[metadatas[Animal.XingZHengQu]] = self.getFieldCon_Text(soup,'td',r'所在地区：')
        lr[metadatas[Animal.JieDaoLu]] =self.getFieldCon_Text(soup,'td',r'项目地址：')
        lr[metadatas[Animal.XiaoQuMing]] = self.getFieldCon_Text(soup,'td',r'项目名称：')
        lr[metadatas[Animal.XiaoQuZhongXinDianZuoBiao]] = lr[metadatas[20]] = self.getbaidugcs(lr[metadatas[6]], lr[metadatas[1]])
        lr[metadatas[Animal.KaiFaShang]] = self.getFieldCon_Text(soup,'td',r'开发单位：')
        lr[metadatas[Animal.ZhanDiMianJi]] = self. getFieldCon_Text(soup,'td',r'项目测算面积')
        lr[metadatas[Animal.URL]] = urlbean.url
        #保存楼盘页面

        SaveFileName = lr[metadatas[Animal.XiaoQuMing]] + "_" +lr[metadatas[Animal.XingZHengQu]] +".html"
        outHtml(self.SaveDir,SaveFileName,webCon)

        louDongReg  = re.compile('title=\'(?P<info>[\s\S]*?)\'\s*id=\'Bd(?P<Id>\d*)\|.*?\'')
        huReg =re.compile('popRoom5\((?P<id>\d*)\)\"[\S\s]*?>(?P<fanghao>\d*)')
        loudongInfos = louDongReg.findall(webCon)
        for loudongInfo in loudongInfos:
            infoarr =  loudongInfo[0].replace("\r\n","").split("·")
            lr[metadatas[Animal.LouDongMing]] =  infoarr[1].split("：")[1].strip() #l楼栋名
            lr[metadatas[Animal.JianZhuJieGou]]  =  infoarr[6].split("：")[1] #建筑结构
            lr[metadatas[Animal.KuoZhanXinXi]]  =  infoarr[2].split("：")[1] #总层数
            husTable = soup.find("table",attrs={"id":re.compile("Bt"+loudongInfo[1] +"|" + lr[metadatas[Animal.LouDongMing]])})
            if( husTable == None):
                husTable = soup.find("table",attrs={"id":re.compile("Bt"+loudongInfo[1] +"|")})
            if( husTable == None):
                print(lr[metadatas[Animal.LouDongMing]])
            else:
                for trr in husTable.find_all('tr'):
                    lr_Ceng = copy.deepcopy(lr)
                    lr_Ceng[metadatas[Animal.LouCengMing]] = trr.find_all('td')[0].text #层名
                    for tdd in trr.findAll('td')[1:]:
                        CengHus = huReg.findall(self.innerHTML(tdd))
                        for cenghu in CengHus:
                            lr_Hu =  copy.deepcopy(lr_Ceng)
                            lr_Hu[metadatas[Animal.FanJianMing]] =cenghu[1] #房间名
                            self.getitem("http://www.wzfg.com/realweb/stat/HouseInfoUser5.jsp?isLimit=&isUni=&houseID=" + cenghu[0],lr_Hu,i_order)


    #解析项目列表
    def getitem(self, url,lr,i_order):
        LOG.info('温州网签 %s_%s 信息', lr[metadatas[Animal.XiaoQuMing]], lr[metadatas[Animal.LouDongMing]])
        #time.sleep(random()+1)
        try:
            r = requests.get(url, headers=self.headers, timeout=(3.05, 20))
        except:
            outTxtLine(File_Operation_Type.a.name,parent_path + "\\OutFile\\","温州网签Error.txt",lr[metadatas[Animal.URL]]  + "\t访问超时")
            return ;
        if(r.status_code != requests.codes.ok and r.status_code != 404):
            LOG.warning('http状态:%s, url %s', r.status_code, url)
            outTxtLine(File_Operation_Type.a.name,parent_path + "\\OutFile\\","温州网签Error.txt", url + "\t"+ str(r.status_code))

        LOG.info('访问耗时:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)


        t1 = time.time()
        webCon_Hu = r.content.decode('gbk', errors='ignore')
        soup = BeautifulSoup(webCon_Hu, 'html.parser') #lxml
        #存储页面信息
        SaveFileName = lr[metadatas[Animal.XiaoQuMing]] + "_" +lr[metadatas[Animal.XingZHengQu]] + "_" + lr[metadatas[Animal.LouDongMing]] + "_" + lr[metadatas[Animal.FanJianMing]] +".html"
        outHtml(self.SaveDir,SaveFileName,webCon_Hu)
        lr[metadatas[Animal.URL]] = lr[metadatas[Animal.URL]] + "," +url
        #解析数据
        lr[metadatas[Animal.Str_Order]] =i_order[:-1]+'3'
        #填充为空的字段
        self.completionlr(lr, metadatas)
        #如果是404楼户信息页面报错就直接存储信息
        if r.status_code == 404:
            lr[metadatas[Animal.KuoZhanXinXi]] = json.dumps(lr[metadatas[Animal.KuoZhanXinXi]], ensure_ascii=False)
            #存储
            outDicCon(File_Operation_Type.a.name,parent_path + "\\OutFile\\","温州网签Info.txt",metadatas,lr)
            return
        ls = []
        #解析状态对应关系
        table_head = []
        try:
            for cell in soup.find('table',attrs={"class":'biankuang'}).find_all('td'):
                #判断出来单元、层、户
                if (cell.text =='设计用途:' ):
                    lr[metadatas[Animal.GuiHuaYongTu]]  = self.getFieldCon_Cell(cell,'设计用途:')
                if (cell.text =='总建筑面积:'):
                    lr[metadatas[Animal.JianZhuMianJi]] = self.getFieldCon_Cell(cell,'总建筑面积:')
                if (cell.text =='套内面积:' ):
                    lr[metadatas[Animal.TaoNeiMianJi]] = self.getFieldCon_Cell(cell,'套内面积:')
                if (cell.text =='分摊面积:' ):
                    lr[metadatas[Animal.GongTanMianJi]] = self.getFieldCon_Cell(cell,'分摊面积:')
                if (cell.text =='一房一价:' ):
                    lr[metadatas[Animal.AnTaoMeiMianDanJia]] = self.getFieldCon_Cell(cell,'一房一价:')
                if (cell.text =='建筑结构:' ):
                    lr[metadatas[Animal.JianZhuJieGou]] =self.getFieldCon_Cell(cell,'建筑结构:')
                #增加在售状态判定
                try:
                    if (cell.text =='户室状态:' ):
                        lr[metadatas[Animal.KuoZhanXinXi]] =  cell.next_sibling.next_sibling.text
                except:
                    lr[metadatas[Animal.KuoZhanXinXi]] = '状态解析异常'
        except:
            outTxtLine(File_Operation_Type.a.name,parent_path + "\\OutFile\\","温州网签Error.txt", url + "\t"+str(r.status_code))
        t2 = time.time()
        LOG.info('解析页面耗时:%f' % (t2-t1))
        #存储
        outDicCon(File_Operation_Type.a.name,parent_path + "\\OutFile\\","温州网签Info.txt",metadatas,lr)


if __name__ == '__main__':
    zzfdc = wwwwzfgcom()
    #得列表链接
    outTxtHeader(File_Operation_Type.a.name,parent_path + "\\OutFile\\","温州网签Info.txt",metadatas)
    ls = zzfdc.GetPageList( 'http://www.wzfg.com/realweb/stat/ProjectSellingList.jsp',94)
    objList = zzfdc.getProjectUrl(ls)
    for url in objList:
        zzfdc.getproject(UrlBean(url, 'wwwwzfgcom#getproject', param={metadatas[58]:{}}, headers={'page':0, 'pname':0}, order='0123456789'))
