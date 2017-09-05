from selenium import webdriver
import os,sys
if __name__ == '__main__':
    parent_path = os.path.dirname(os.getcwd()) #获取当前工作目录，也就是在哪个目录下运行这个程序
    sys.path.append(parent_path)
index =7934
from Common.OutHtml import *
from Common.OutTxt import *

file_object = open('D:\\网签\\济南楼栋的户列表Url.txt','r',encoding= 'utf-8')
lines = file_object.readlines()

for url in lines[7934:]:
    try:
        ff = webdriver.PhantomJS()
        ff.get(url)
        htmlCon = ff.page_source
        outHtml(parent_path+"\\济南\\",str(index)+".html",htmlCon)
        outTxtLine('a',parent_path+"\\济南\\", 'mapping.txt', str(index) + "\t" +url)
        index = index + 1
    except:
        outTxtLine('a',parent_path+"\\济南\\", 'error.txt',url)
