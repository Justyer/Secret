import datetime, json, copy
import re
from random import random
from enum import Enum


import sys, os
parent_path = os.path.dirname(os.getcwd())
sys.path.append(parent_path)

from util.UtilityGcs import GcsConverUtil
from webparser.webparserbase import ParserBase
from serializ.htmlfile import *
from bean.urlbean import *
from log.logger import *

metadatas = ('省','城市','行政区','区域','街道路','路牌号','小区名','小区别名','楼栋名','楼栋别名',
             '楼栋街牌号','单元名','单元别名','单元街牌号','楼层名','楼层别名','房间名','房间别名','房间街牌号','小区坐标中心点坐标',
             '小区边界坐标','楼栋坐标','单元坐标','数据来源','开发商','总建筑面积','占地面积','房屋所有权证号','总户数','车位数量', #29
             '绿化率','容积率','总栋数','土地使用权证号','发证日期','地上层数','地下层数','建筑高度','规划用途','户型', #40
             '建筑面积','套内面积','公摊面积','按建面单价','按套内面单价','总价','朝向','小区id','小区评估系数','小区评估参数',
             '竣工年限','楼盘案例均价','楼栋id','建筑结构','房号','建筑类别','房屋结构','房屋户评估系数','扩展信息','STR_ORDER','URL')

class Animal:
    Sheng = 0  #'省'
    Chengshi  = 1 #'城市'
    XingZHengQu = 2 #'行政区'
    Quyu = 3 #'区域'
    JieDaoLu =4 #街道路
    LuPaiHao =5  #路牌号
    XiaoQuMing = 6 #小区名
    XiaoQuBieMing = 7 #小区别名
    LouDongMing = 8 #楼栋名
    LouDongBieMing =9 #楼栋别名
    LouDongJiePaiHao = 10 #楼栋街牌号
    DanYuanMing = 11 #单元名
    DanYuanBieMing = 12 #单元别名
    DanYuanJieBaiHao = 13 #单元街牌号
    LouCengMing = 14 #楼层名
    LouCengBieMing = 15 #楼层别名
    FanJianMing = 16 #房间名
    FanJianBieMing = 17 #房间别名
    FangJianJiePaiHap = 18 # 房间街牌号
    XiaoQuZhongXinDianZuoBiao  =19  #小区坐标中心点坐标
    XiaoQuBianJieZuoBiao = 20  #小区边界坐标
    LouDongZuoBiao = 21 #楼栋坐标
    DanYuanZuoBiao = 22 #单元坐标
    ShuJuLaiYuan = 23 # 数据来源
    KaiFaShang = 24 #开发商
    ZongJianZhuMianJi = 25  #总建筑面积
    ZhanDiMianJi = 26 #占地面积
    FangWuSuoYouQuanZhengHao = 27 #房屋所有权证号
    ZongHuShu = 28 #总户数
    CheWeiShuLiang = 29 #车位数量
    Lvlualv = 30 #绿化率
    RongJiLv = 31 #容积率
    ZongDongShu = 32 #总栋数
    TuDiShiYongQuanZhengHao = 33 #土地使用权证号
    FaZhengRiqi = 34 #发证日期
    DiShangCengShu = 35 #地上层数
    DiXia = 36 #地下层数
    JianZhuGaoDu =37 # 建筑高度
    GuiHuaYongTu = 38 #规划用途
    HuXing  = 39 #户型
    JianZhuMianJi = 40 #建筑面积
    TaoNeiMianJi = 41 #套内面积
    GongTanMianJi = 42 #公摊面积
    AnJianMianDanJia =43 #按建面单价
    AnTaoMeiMianDanJia = 44 #按套内面单价
    ZongJia = 45 #总价
    ChaoXiang = 46 #朝向
    XiaoQuID = 47 #小区id
    XiaoQuPingJiaXiShu = 48 #小区评估系数
    XiaoQuPingJiaCanShu = 49 #小区评估参数
    JunGongNianXian = 50  #竣工年限
    LouPanAnLiJunJia = 51 #楼盘案例均价
    LouDongID = 52 #楼栋id
    JianZhuJieGou = 53 #建筑结构
    FangHao = 54 #房号
    JianZhuLeiBie = 55 #建筑类别
    FangWuJieGou = 56 #房屋结构
    FangWuPingGuXiShu  = 57 #房屋户评估系数
    KuoZhanXinXi = 58 #扩展信息
    Str_Order = 59 #STR_ORDER
    URL = 60 #URL



class BaseClass:
    headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36 LBBROWSER', 'Connection': 'keep-alive'}
    htmlwrite = HtmlFile()

    @classmethod
    def getFieldCon_Text(self,soup,fieldName,TxtReg):
        reg = re.compile(TxtReg)
        try:
            return soup.find(fieldName, text=reg).next_sibling.next_sibling.text
        except:
          return ""
    @classmethod
    def getFieldCon_Cell(self,Cell,KeyWord):
        try:
            Cell_Text = Cell.text
            Cell_Text =Cell_Text.replace("\n","").replace("\r","").strip()
            if (Cell_Text == KeyWord ):
                return Cell.next_sibling.next_sibling.text.replace("\n","").replace("\r","").strip()
        except:
           pass

    @classmethod
    def MoveChar(self, str):
        return  str.replace("\n","").replace("\r","").replace(" ","").strip()
    @classmethod
    def innerHTML(self,Html_element):
        return "".join([str(x) for x in Html_element.contents])

    @classmethod
    def __init__(self):
        pass


