#东莞市
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import sys, os
import requests, re, urllib.parse
from bs4 import BeautifulSoup, Tag, NavigableString
if __name__ == '__main__':
    parent_path = os.path.dirname(os.getcwd()) #获取当前工作目录，也就是在哪个目录下运行这个程序
    sys.path.append(parent_path)

from Common.BaseClass import  *
from Common.OutTxt import *
from Common.OutHtml import *
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from webparser.webparserbase import ParserBase
LOG=logging.getLogger()
LOG.handlers[0].setLevel(logging.INFO)
LOG.handlers[1].setLevel(logging.INFO)
#driver = webdriver.Firefox()
#解析东莞网签数据
data = {'__VIEWSTATE':"/wEPDwUJLTY3Mjk0MTkwD2QWAgIDD2QWAgIDDxAPFgYeDURhdGFUZXh0RmllbGQFCFRvd25OYW1lHg5EYXRhVmFsdWVGaWVsZAUIVG93bkNvZGUeC18hRGF0YUJvdW5kZ2QQFSIS5Lic6I6e5biC6I6e5Z+O5Yy6EuS4nOiOnuW4guS4nOWfjuWMuhLkuJzojp7luILkuIfmsZ/ljLoS5Lic6I6e5biC5Y2X5Z+O5Yy6EuS4nOiOnuW4guefs+m+memVhxLkuJzojp7luILomY7pl6jplYcS5Lic6I6e5biC5Lit5aCC6ZWHFeS4nOiOnuW4guacm+eJm+WiqemVhxLkuJzojp7luILpurvmtozplYcS5Lic6I6e5biC55+z56Kj6ZWHEuS4nOiOnuW4gumrmOWfl+mVhxLkuJzojp7luILpgZPmu5jplYcS5Lic6I6e5biC5rSq5qKF6ZWHEuS4nOiOnuW4gumVv+WuiemVhxLkuJzojp7luILmspnnlLDplYcS5Lic6I6e5biC5Y6a6KGX6ZWHEuS4nOiOnuW4guadvuWxsea5lhLkuJzojp7luILlr67mraXplYcV5Lic6I6e5biC5aSn5bKt5bGx6ZWHEuS4nOiOnuW4guWkp+acl+mVhxLkuJzojp7luILpu4TmsZ/plYcV5Lic6I6e5biC5qif5pyo5aS06ZWHEuS4nOiOnuW4guWHpOWyl+mVhxLkuJzojp7luILloZjljqbplYcS5Lic6I6e5biC6LCi5bKX6ZWHEuS4nOiOnuW4gua4hea6qumVhxLkuJzojp7luILluLjlubPplYcS5Lic6I6e5biC5qGl5aS06ZWHEuS4nOiOnuW4guaoquaypemVhxLkuJzojp7luILkuJzlnZHplYcS5Lic6I6e5biC5LyB55+z6ZWHEuS4nOiOnuW4guefs+aOkumVhxLkuJzojp7luILojLblsbHplYcS5Lic6I6e5biC6JmO6Zeo5rivFSIBMQEyATQBOAIxNgIzMgI2NAMxMjgDMjU2AzUxMgQxMDI0BDIwNDgENDA5NgQ4MTkyBTE2Mzg0BTMyNzY4CjQyOTQ5NjcyOTYFNjU1MzYGMTMxMDcyBjI2MjE0NAY1MjQyODgHMTA0ODU3NgcyMDk3MTUyBzQxOTQzMDQHODM4ODYwOAgxNjc3NzIxNggzMzU1NDQzMgg2NzEwODg2NAkxMzQyMTc3MjgJMjY4NDM1NDU2CTUzNjg3MDkxMgoxMDczNzQxODI0CjIxNDc0ODM2NDgKODU4OTkzNDU5MhQrAyJnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZGRkj8BjIqM3rC5YfLrDm9g7Tu0Uvk8=",
        '__EVENTVALIDATION':"/wEWMAKX14miCgLRwJ/XAwLQwJ/XAwLSwJ/XAwLGwJ/XAwLRwOfUAwLTwNfUAwLUwO/UAwKPy6OpBQKUipmABwKFr/BdAoGvjPwOAsr80YwBArfisekLAqvi5YUIAoLgvAsC3NvNtwECrcL7+gkC9Y/YywwC99LEiQoCtsqy0wkCsZi6hA0Cqt/MoQgChpH80QgC5Jr1nAwC+qjqgQEC8M739QoCm8GHuggCn5Tm5w0C9tbCqAUC6daBqAMC6ompmA8C06/64QwC5Kmahg0C2ObA1gUCi9PWkQMC6qrBowMCjoDBuwMC0ZbVXQK5ge32DAKxqoqLAwKxiayuCAK5iZTwAQLjge3eCQLX88kKAtjzyQoC8IG2iAYC482n8gfOL6UmolwOFapomTdmLkjlnWYqsw==",
        'townName':"1",'usage':"",'projectName':"",'projectSite':"",'developer':"",'area1':"",'area2':"",'resultCount':"140",'pageIndex':"0"}
class dgfcdggovcnpy(ParserBase,BaseClass):
        def __init__(self):
            super(dgfcdggovcnpy, self).__init__()
        SaveDir =parent_path + "\\OutFile\\东莞房产管理局\\"
        reg_url = re.compile(("href=\"(?P<url>.*?)\""))
        reg_楼盘  = re.compile('href=\"(?P<url>.*?)\"')
        def GetPageList(self, url):
            file_object = open(parent_path + "\\OutFile\\区镇ID.txt",'r',encoding= 'utf-8')
            lines = file_object.readlines()
            ls = {}
            for id in lines:
                try:
                    data['townName'] = id.replace('\n',"").replace("\ufeff","").strip()
                    r = requests.post(url,data=data)
                    html = r.content.decode('utf8')
                    soup = BeautifulSoup(html, 'html.parser') #lxml
                    resultTable =  soup.find("table",attrs={"id":re.compile('resultTable')})
                    SaveFileName = data['townName']  +".html"
                    outHtml(self.SaveDir,SaveFileName,html)
                    list_楼盘 = self.reg_楼盘.findall(self.innerHTML(resultTable))
                    for s楼盘 in list_楼盘:
                       subUrl= "http://dgfc.dg.gov.cn/dgwebsite_v2/Vendition/" + s楼盘.replace("amp;","")
                       if((subUrl in ls)== False):
                            ls[subUrl] =1
                            outTxtLine('a',parent_path+"\\OutFile\\", '东莞楼盘List.txt',subUrl + "\t"  +data['townName'])
                            self.getProjectUrl(subUrl,data['townName'])
                except :
                    error_info=sys.exc_info()
                    outTxtLine('a',parent_path+"\\OutFile\\", '东莞网签Error.txt',url + "\t" +data['townName'] )
            return ls

        #解析列表分页信息
        def getProjectUrl(self, url,id):
            try:
                lr = {metadatas[58]:{}}
                lr[metadatas[Animal.Sheng]] = '广东'
                lr[metadatas[Animal.Chengshi]] = '东莞'
                reg_Name=re.compile("开发单位：</b>(?P<danwei>.*?)<[\s\S]*?项目名称：</b>(?P<xiangmu>[\s\S]*?)<")

                r = requests.get(url, headers=self.headers, timeout=(3.05, 10))
                if(r.status_code != requests.codes.ok):
                    LOG.warning('http状态:%s, url %s', r.status_code, url)
                    outTxtLine(File_Operation_Type.a.name,parent_path + "\\OutFile\\","东莞网签Error.txt",url + "\t"+r.status_code)
                html = r.content.decode('utf8')
                soup = BeautifulSoup(html, 'html.parser') #lxml
                con_楼盘 = reg_Name.findall(html)
                lr[metadatas[Animal.KaiFaShang]] =con_楼盘[0][0]
                lr[metadatas[Animal.XiaoQuMing]] =con_楼盘[0][1].replace('\n',"").replace("\r","").strip()


                SaveFileName = id + "_" + lr[metadatas[Animal.XiaoQuMing]] +".html"
                outHtml(self.SaveDir,SaveFileName,html)
                self.completionlr(lr, metadatas)
                for tr in soup.find("table",attrs={"id":re.compile('houseTable_')}).find_all('tr')[1:]:
                    tdList = tr.find_all("td")
                    lr[metadatas[Animal.JieDaoLu]] =tdList[1].text
                    lr[metadatas[Animal.GuiHuaYongTu]] =tdList[4].text
                    lr[metadatas[Animal.ZongHuShu]] =tdList[3].text
                    lr[metadatas[Animal.DiShangCengShu]] = tdList[2].text
                    DongUrl = self.reg_url.findall(self.innerHTML(tr))
                    lr_Dong = copy.deepcopy(lr)
                    self.getDong("http://dgfc.dg.gov.cn/dgwebsite_v2/Vendition/" + DongUrl[0].replace("amp;",""),lr_Dong,id)
            except:
                error_info=sys.exc_info()
                outTxtLine(File_Operation_Type.a.name,parent_path + "\\OutFile\\","东莞网签Error.txt",url + "\t" + lr[metadatas[Animal.XiaoQuMing]] + "\t" + id)


        #解析项目列表
        def getDong(self, url,lr,id):
            try:
                LOG.info('东莞网签 %s_%s 信息', lr[metadatas[Animal.XiaoQuMing]], lr[metadatas[Animal.LouDongMing]])
                r = requests.get(url, headers=self.headers, timeout=(3.05, 10))
                if(r.status_code != requests.codes.ok):
                    LOG.warning('http状态:%s, url %s', r.status_code, urlbean.url)
                    outTxtLine(File_Operation_Type.a.name,parent_path + "\\OutFile\\","东莞网签Error.txt",url + "\t"+r.status_code)
                html = r.content.decode('utf8')
                SaveFileName = str(id) + "_" +lr[metadatas[Animal.XiaoQuMing]] +"_楼盘表.html"
                outHtml(self.SaveDir,SaveFileName,html)
                soup = BeautifulSoup(html, 'html.parser') #lxml
                table = soup.find("table",attrs={"id":re.compile('roomTable')})
                if(table == None):
                    outDicCon(File_Operation_Type.a.name,parent_path + "\\OutFile\\","东莞网签Info.txt",metadatas,lr)
                    return
                for tr in table.find_all('tr')[1:]:
                    tdList = tr.find_all("td")
                    lr[metadatas[Animal.LouCengMing]] =tdList[0].text
                    for td in tdList[1:]:
                         subtdList = td.find_all("td")
                         for subtd in subtdList:
                             lr[metadatas[Animal.FanJianMing]] = subtd.text
                             huUrl = self.reg_url.findall(self.innerHTML(subtd))
                             lr_Hu = copy.deepcopy(lr)
                             self.getitem("http://dgfc.dg.gov.cn/dgwebsite_v2/Vendition/" + huUrl[0].replace("amp;",""),lr_Hu,id)
            except:
                error_info=sys.exc_info()
                outTxtLine(File_Operation_Type.a.name,parent_path + "\\OutFile\\","东莞网签Error.txt",url + "\t" + lr[metadatas[Animal.XiaoQuMing]] + "\t" + id)
                outDicCon(File_Operation_Type.a.name,parent_path + "\\OutFile\\","东莞网签Info.txt",metadatas,lr)

        def getitem(self, url,lr,id):
            try:
                r = requests.get(url, headers=self.headers, timeout=(3.05, 10))
                if(r.status_code != requests.codes.ok):
                    LOG.warning('http状态:%s, url %s', r.status_code, urlbean.url)
                    outTxtLine(File_Operation_Type.a.name,parent_path + "\\OutFile\\","东莞网签Error.txt",url + "\t"+r.status_code)
                html = r.content.decode('utf8')
                SaveFileName = id + "_" +lr[metadatas[Animal.XiaoQuMing]] +"_楼盘表" + lr[metadatas[Animal.FanJianMing]]+ ".html"
                outHtml(self.SaveDir,SaveFileName,html)
                soup = BeautifulSoup(html, 'html.parser') #lxml
                div = soup.find("div",attrs ={"class", "content"})
                if(div == None):
                    outDicCon(File_Operation_Type.a.name,parent_path + "\\OutFile\\","东莞网签Info.txt",metadatas,lr)
                    return
                for  cell in div.find_all("td"):
                    if(self.MoveChar(cell.text) == '建筑面积：'):
                        lr[metadatas[Animal.JianZhuMianJi]] = self.getFieldCon_Cell(cell,'建筑面积：')
                    if(self.MoveChar(cell.text) == '套内面积：'):
                        lr[metadatas[Animal.TaoNeiMianJi]] = self.getFieldCon_Cell(cell,'套内面积：')
                    if(self.MoveChar(cell.text) == '分摊面积：'):
                        lr[metadatas[Animal.GongTanMianJi]] = self.getFieldCon_Cell(cell,'分摊面积：')
                outDicCon(File_Operation_Type.a.name,parent_path + "\\OutFile\\","东莞网签Info.txt",metadatas,lr)
            except:
                error_info=sys.exc_info()
                outTxtLine(File_Operation_Type.a.name,parent_path + "\\OutFile\\","东莞网签Error.txt",url)

if __name__ == '__main__':
    zzfdc = dgfcdggovcnpy()
    #得列表链接
    outTxtHeader(File_Operation_Type.a.name,parent_path + "\\OutFile\\","东莞网签Info.txt",metadatas)
    zzfdc.GetPageList( 'http://dgfc.dg.gov.cn/dgwebsite_v2/Vendition/ProjectInfo.aspx?new=1')

