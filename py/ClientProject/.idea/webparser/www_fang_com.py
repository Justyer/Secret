# coding=gbk
#�������Ե���·��
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
# metadatas = ('����','��Դ����','С������','��������','С������','¥������','��ַ','�������',                  #7
#             '��¥��','��ǰ��','����','�������','ʹ�����','��Ȩ����','װ�����','����','��������',            #16
#             '��������','����������','��������','��̨����','����','�ܼ�','����ʱ��','����ͼƬ','��Ϣ��Դ',      #25
#             '��ϵ��','���͹�˾','�绰����','γ��','����','����ʱ��','סլ���','�������','������ʩ','��ͨ״��', #35
#             '¥����ҵ����','¥���̻���','¥����ҵ��','������Դ','����','������','str_order')                    #41

metadatas = ('��Ϣ��Դ','����','������','Ƭ��','��Դ����','����','С������','С������','��ַ','�������','����',                     #10
             '¥��','��¥��','��ǰ��','����','�������','ʹ�����','����','��������','��������','����������',                        #20
             '��������','��̨����','�ܼ�','����','���¾���','С�����̵���','סլ���','��Ȩ����','װ�����','�������',               #30
             '¥����ҵ����','С�����','��ϵ��','��ϵ������','���͹�˾','�ŵ�','�绰����','������Ȧ','ע��ʱ��','���͹�˾��Դ���',    #40
             '����ʱ��','С���ܻ���','С���ܽ������','�ݻ���','С����ͣ��λ','������','��ͨ״��','������ʩ','¥���̻���','��ҵ��˾',  #50
             '¥����ҵ��','����ʹ������','��ס��','ѧУ','���ϲ���','��԰���','���������','��������','��λ����','���ṹ',           #60
             '����','����ͼƬ','γ��','����','str_order','������Դ')                                                                                      #65

import socket,time
#socket.timeout = 3
import requests, re
from bs4 import BeautifulSoup, Tag
from requests.exceptions import RequestException
class myException(Exception):pass
#�����ѷ���վ
class wwwfangcom(ParserBase):
    htmlwrite = HtmlFile()
    headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36 LBBROWSER', 'Connection': 'keep-alive'}
    shi = re.compile(r'(\d+)��|��|����')
    ting = re.compile(r'(\d+)��')
    wei = re.compile(r'(\d+)��')
    chu = re.compile(r'(\d+)��')
    yangtai = re.compile(r'(\d+)̨|��̨')

    pagenotfound = '��Դ�����ڣ�'

    t_90 = ('����','�Ϻ�')
    t_45 = ('����','����','����')
    t_30 = ('���',)
    t_25 = ('����',)
    t_15 = ('����','�ɶ�','�Ͼ�','�ൺ','����','֣��','�麣','�人','����','��ݸ')
    t_7  = ('����','����','����','����','ʯ��ׯ','�Ϸ�','��ɳ','����','����','��̨','����','̫ԭ',
            '����','����','���ͺ���','������','����','����','��ɽ','����','����','����','����',
            '����','��ɽ','�ȷ�','����','����','�ϲ�','����','��ͨ','�ػʵ�','Ȫ��','����','̩��','��ɽ','Ϋ��','����',
            '��̶','����','����','����','�˲�','����','��ɽ',
            '����','��','����','��³ľ��','����','�Ž�','����','����','����', '����', '��ɽ', 'ʯ����', '����', '���Ǹ�',
            '��ˮ','����','����','��ʯ','����','����','������','����')

    #�ṩ��С���нű��жϳ���
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
        LOG.info('�ѷ�Ĭ�Ϸ�����ó����б�!')
        r = requests.get(urlbase.url, headers=self.headers, timeout=(3.05, 3.5))
        LOG.info('���ʺ�ʱ:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwfangcom %s ����״̬:%s', urlbase.url, r.status_code)
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
                    LOG.info('��ó���%sҳ����Ϣ%s', i.text, i['href']+'/house/h316-i3'+str(i_count)+'-j3100/')
                    i_count += 1
            elif i.text in self.t_45:
                i_count = 1
                while i_count <= 45:
                    ls.append(UrlBean(i['href']+'/house/h316-i3'+str(i_count)+'-j3100/', self.message('getpages'), param=i_count, headers=i.text, order=i_order))
                    LOG.info('��ó���%sҳ����Ϣ%s', i.text, i['href']+'/house/h316-i3'+str(i_count)+'-j3100/')
                    i_count += 1
            elif i.text in self.t_30:
                i_count = 1
                while i_count <= 30:
                    ls.append(UrlBean(i['href']+'/house/h316-i3'+str(i_count)+'-j3100/', self.message('getpages'), param=i_count, headers=i.text, order=i_order))
                    LOG.info('��ó���%sҳ����Ϣ%s', i.text, i['href']+'/house/h316-i3'+str(i_count)+'-j3100/')
                    i_count += 1
            elif i.text in self.t_25:
                i_count = 1
                while i_count <= 25:
                    ls.append(UrlBean(i['href']+'/house/h316-i3'+str(i_count)+'-j3100/', self.message('getpages'), param=i_count, headers=i.text, order=i_order))
                    LOG.info('��ó���%sҳ����Ϣ%s', i.text, i['href']+'/house/h316-i3'+str(i_count)+'-j3100/')
                    i_count += 1
            elif i.text in self.t_15:
                i_count = 1
                while i_count <= 15:
                    ls.append(UrlBean(i['href']+'/house/h316-i3'+str(i_count)+'-j3100/', self.message('getpages'), param=i_count, headers=i.text, order=i_order))
                    LOG.info('��ó���%sҳ����Ϣ%s', i.text, i['href']+'/house/h316-i3'+str(i_count)+'-j3100/')
                    i_count += 1
            elif i.text in self.t_7:
                i_count = 1
                while i_count <= 7:
                    ls.append(UrlBean(i['href']+'/house/h316-i3'+str(i_count)+'-j3100/', self.message('getpages'), param=i_count, headers=i.text, order=i_order))
                    LOG.info('��ó���%sҳ����Ϣ%s', i.text, i['href']+'/house/h316-i3'+str(i_count)+'-j3100/')
                    i_count += 1
        return ls

    #�������ж��ַ��б�ҳ
    def getpages(self, urlbase):
        LOG.info('fanggetpages��ó���%s���ַ��б���Ϣ', urlbase.url)
        r = requests.get(urlbase.url, headers=self.headers, timeout=(3.05, 3.5))
        LOG.info('���ʺ�ʱ:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwfangcom %s ����״̬:%s', urlbase.url, r.status_code)
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
                LOG.debug('%s��%dҳ%d��' % (urlbase.headers, urlbase.param, itemIndex))
                itemIndex += 1
        #���ڷ�ҳ��Ϣ
        # if urlbase.param and urlbase.param<=self.fetchpage:
        #     #�����һҳ��ַ
        #     nextpage = soup.find('div', id='list_D10_15')
        #     if nextpage:
        #         nextpageurl = nextpage.find('a', id ='PageControl1_hlk_next')
        #         if nextpageurl:
        #             list.append(UrlBean(host+nextpageurl['href'], self.message('getpages'), param=urlbase.param+1, headers=urlbase.headers))
        #             LOG.debug('%s��%dҳ' % (urlbase.headers, urlbase.param))
        return ls

    #������ϸҳ����Ϣ
    #@retries(10, delay=1, backoff=1, exceptions=(RequestException))
    def getitem(self, urlbase):
        LOG.info('fanggetinfo��ó���%s������ϸ��Ϣ', urlbase.url)
        r = requests.get(urlbase.url, headers=self.headers, timeout=(3.05, 3.5))
        LOG.info('���ʺ�ʱ:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        self.htmlwrite.save('%s\\%s\\%s' %(self.__class__.__name__, '���ַ�', urlbase.param), r.url, r.text)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwfangcom %s ����״̬:%s', urlbase.url, r.status_code)
            return
        soup = BeautifulSoup(r.content.decode('gbk', errors='ignore'), 'html.parser') #lxml
        #������ص��Ƿ�Դ������ҳ���ֱ���˳�
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
            lr[metadatas[41]] = _strip(title_bs.find(text=time_regexp).string.replace('����ʱ�䣺', ''))
        except:
            lr[metadatas[41]] = ''

        city_Bs = soup.find('div', attrs={'class':'bread'})

        if city_Bs is not None:
            city = city_Bs.find_all('a')
            lr[metadatas[61]] = (">".join([_strip(dd.text) for dd in city])).replace('���ַ�', '').strip()
        try:
            lr[metadatas[1]] = _strip(city[1].string.replace('���ַ�', ''))
        except:
            lr[metadatas[1]] = ''
        try:
            lr[metadatas[2]] = _strip(city[2].string.replace('���ַ�', ''))
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
                        lr[metadatas[35]] = re.findall('��<span class="pl24">˾</span>��(.*?)</li>',reTextjjr,re.S)[0]
                    except:
                        lr[metadatas[35]] = ''
                    try:
                        lr[metadatas[36]] = re.findall('<li>�ŵ����ƣ�(.*?)</li>',reTextjjr,re.S)[0]
                    except:
                        lr[metadatas[36]] = ''
                    try:
                        lr[metadatas[38]] = re.findall('������Ȧ��(.*?)</li>',reTextjjr,re.S)[0]
                        if '</dd>' in lr[metadatas[38]]:
                            lr[metadatas[38]] = _split(lr[metadatas[38]],'</dd>',0)
                    except:
                        lr[metadatas[38]] = ''
                    try:
                        lr[metadatas[39]] = re.findall('<li>ע��ʱ�䣺(.*?)</li>',reTextjjr,re.S)[0]
                    except:
                        lr[metadatas[39]] = ''
                else:
                    try:
                        lr[metadatas[35]] = re.findall('</b><span class="">(.*?)</span>',reTextjjr,re.S)[0]
                    except:
                        lr[metadatas[35]] = ''
                    try:
                        md = re.findall('<li>�����ŵ꣺(.*?)</span>',reTextjjr,re.S)[0]
                        dr = re.compile(r'<[^>]+>',re.S)
                        lr[metadatas[36]] =  _strip(re.sub(dr,'',md))
                    except:
                        lr[metadatas[36]] = ''
                    try:
                        sq = re.findall('<li>������Ȧ��(.*?)</span>',reTextjjr,re.S)[0]
                        dr = re.compile(r'<[^>]+>',re.S)
                        lr[metadatas[38]] =  _strip(re.sub(dr,'',sq))
                        if '</dd>' in lr[metadatas[38]]:
                            lr[metadatas[38]] = _split(lr[metadatas[38]],'</dd>',0)
                    except:
                        lr[metadatas[38]] = ''
                    try:
                        rzsj = re.findall('��ְʱ�䣺(.*?)</li>',reTextjjr,re.S)[0]
                        dr = re.compile(r'<[^>]+>',re.S)
                        lr[metadatas[39]] =  _strip(re.sub(dr,'',rzsj))
                    except:
                        lr[metadatas[39]] = ''
        else:
            try:
                lr[metadatas[33]] = soup.find('div', class_='bookTel').find('a', class_='name').getText(strip=True).replace('ҵ��', '')
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
            lr[metadatas[40]] = re.findall('<span class="mr10">��Դ��ţ�(.*?)</span>',reText,re.S)[0]
        except:
            lr[metadatas[40]] = ''

        inforTxt_bs = soup.find('div', attrs={'class': 'inforTxt'})
        try:
            lr[metadatas[23]] = _strip(inforTxt_bs.find('span', {'class': 'red20b'}).string)
        except:
            lr[metadatas[23]] = ''
        try:
            lr[metadatas[24]] = _split(inforTxt_bs.dl.dt.text, '(', 1).split(')')[0].replace('Ԫ/�O', '')
            if lr[metadatas[24]] == '':
                lr[metadatas[24]] = _split(inforTxt_bs.dl.dt.text, '��', 1).split('��')[0].replace('Ԫ/�O', '')
        except:
            lr[metadatas[24]] = ''
        fit_str = "".join([dd.text for dd in inforTxt_bs.find('dl').find_all('dd')])
        # print('fit_str', fit_str)
        try:
            lr[metadatas[17]] = _split(fit_str, '���ͣ�', 1).split('���������')[0]
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
            lr[metadatas[15]] = _split(fit_str, '���������', 1).split('ʹ�������')[0].replace('O', '').replace('�O','')
        except:
            lr[metadatas[15]] = ''
        try:
            lr[metadatas[16]] = _split(fit_str, 'ʹ�������', 1).split('O')[0].replace('O', '').replace('�O','')
        except:
            lr[metadatas[16]] = ''
        if '���' in lr[metadatas[16]]:
            lr[metadatas[16]] = ''
        try:
            dls = inforTxt_bs.find_all('dl')
            str_next_dl = (dls[1] if len(dls)>=2 else dls[0]).text
        except Exception as e:
            str_next_dl = ''
        lr[metadatas[9]] = _split(str_next_dl, '�����', 1).split('��')[0].strip()
        #louceng = _split(str_next_dl.replace("��", ")"), '¥�㣺', 1).split(')')[0].strip()+')'
        try:
            louceng = re.search('¥�㣺([^)��]*[)��])', str_next_dl).group(1)
            lr[metadatas[11]] = louceng
            if '����' in lr[metadatas[11]]:
                lr[metadatas[11]] = lr[metadatas[11]].split('����')[0]
        except:
            lr[metadatas[11]] = ''
        try:
            lr[metadatas[12]] = re.findall('��(.*?)��',louceng,re.S)[0]
            lr[metadatas[13]] = re.findall('��(.*?)��',louceng,re.S)[0]
        except:
            lr[metadatas[12]] = ''
            lr[metadatas[13]] = ''

        lr[metadatas[30]] = _split(str_next_dl, '�������', 1).split('��Ȩ���ʣ�')[0].strip()
        #lr[metadatas[27]] = _split(str_next_dl, 'סլ���', 1).split('լ')[0].strip().replace(',','')+'լ'
        try:
            lr[metadatas[27]] = inforTxt_bs.find('span', text=re.compile(r'סլ���')).parent.getText(strip=True).replace('סլ���', '')
        except:
            lr[metadatas[27]] = ''
        lr[metadatas[28]] = _split(str_next_dl, '��Ȩ���ʣ�', 1).split('¥�����ƣ�')[0].strip().replace(',','')
        lr[metadatas[29]] = _split(str_next_dl, 'װ�ޣ�', 1).split('סլ���')[0].strip()
        if '�������' in lr[metadatas[29]]:
            lr[metadatas[30]] = _split(lr[metadatas[29]], 'װ�������', 1).split('��Ȩ���ʣ�')[0]
            lr[metadatas[28]] = _split(lr[metadatas[29]], '��Ȩ���ʣ�', 1).split('¥�����ƣ�')[0]
            lr[metadatas[29]] = _split(lr[metadatas[29]], '�������', 0)
        elif '��Ȩ����' in lr[metadatas[29]]:
            lr[metadatas[29]] = _split(lr[metadatas[29]], '��Ȩ���ʣ�', 0)
        lr[metadatas[14]] = _split(str_next_dl,'����',1).split('¥�㣺')[0].strip()
        # ���ϲ���
        try:
            lr[metadatas[55]] = inforTxt_bs.find('span', text=re.compile(r'���ϲ�����')).parent.getText(strip=True).replace('���ϲ�����', '').replace('��', '')
        except:
            lr[metadatas[55]] = ''
        try:
            lr[metadatas[58]] = inforTxt_bs.find('span', text=re.compile(r'����������')).parent.getText(strip=True).replace('����������', '').replace('��', '')
        except:
            lr[metadatas[58]] = ''
        if '���ϲ���' in lr[metadatas[14]]:
            #lr[metadatas[55]] = _split(lr[metadatas[14]], '���ϲ�����', 1).split('װ�޳̶ȣ�')[0]
            lr[metadatas[56]] = _split(lr[metadatas[14]], '��԰�����', 1).split('����������')[0]
            if '���ṹ' in lr[metadatas[56]]:
                lr[metadatas[60]] = lr[metadatas[56]].split('���ṹ��')[1].strip()
                if '��λ������' in lr[metadatas[60]]:
                    lr[metadatas[60]] = _split(lr[metadatas[60]], '��λ������', 0)
                lr[metadatas[56]] = lr[metadatas[56]].split('���ṹ��')[0].strip()
            if '�����������' in lr[metadatas[56]]:
                lr[metadatas[56]] = lr[metadatas[56]].split('�����������')[0].strip()
            lr[metadatas[57]] = _split(lr[metadatas[14]], '�����������', 1).split('¥�����ƣ�')[0]
            #lr[metadatas[58]] = _split(lr[metadatas[14]], '����������', 1).split('��λ������')[0]
            # if '¥�����ƣ�' in lr[metadatas[58]]:
            #     lr[metadatas[58]] = lr[metadatas[58]].split('¥�����ƣ�')[0].strip()
            lr[metadatas[59]] = _split(lr[metadatas[14]], '��λ������', 1).split('�����������')[0]
            if '¥�����ƣ�' in lr[metadatas[59]]:
                lr[metadatas[59]] = lr[metadatas[59]].split('¥�����ƣ�')[0].strip()
            lr[metadatas[29]] = _split(lr[metadatas[14]], 'װ�޳̶ȣ�', 1).split('������ʽ��')[0]
            if len(lr[metadatas[29]])>7:
                lr[metadatas[29]] = lr[metadatas[29]].split('��')[0].replace(',','')+'��'
            lr[metadatas[30]] = _split(lr[metadatas[14]], '������ʽ��', 1).split('�����')[0]
            if '���ṹ' in lr[metadatas[30]]:
                lr[metadatas[30]] = lr[metadatas[30]].split('���ṹ��')[0]
            elif '��������' in lr[metadatas[30]]:
                lr[metadatas[30]] =lr[metadatas[30]].split('����������')[0]
            elif '��λ����' in lr[metadatas[30]]:
                lr[metadatas[30]] = lr[metadatas[30]].split('��λ������')[0]
            elif '���������' in lr[metadatas[30]]:
                lr[metadatas[30]] = lr[metadatas[30]].split('�����������')[0]
            elif '¥������' in lr[metadatas[30]]:
                lr[metadatas[30]] = lr[metadatas[30]].split('¥�����ƣ�')[0]
            if '¥�����ƣ�' in lr[metadatas[30]]:
                lr[metadatas[30]] = lr[metadatas[30]].split('¥�����ƣ�')[0].strip()
            lr[metadatas[14]] = lr[metadatas[14]].split('���ϲ���')[0]
        elif '�ṹ��' in lr[metadatas[14]]:
            lr[metadatas[14]] = lr[metadatas[14]].split('�ṹ')[0]
        elif 'װ�ޣ�' in lr[metadatas[14]]:
            lr[metadatas[14]] = lr[metadatas[14]].split('װ��')[0]
        elif '�����' in lr[metadatas[14]]:
            lr[metadatas[14]] = lr[metadatas[14]].split('���')[0]
        elif 'С����' in lr[metadatas[14]]:
            lr[metadatas[14]] = lr[metadatas[14]].split('С��')[0]
        if '¥��' in lr[metadatas[15]]:
            #150¥�㣺�в㣨��18�㣩�����ϱ�װ�ޣ�ë�������2014��
            if '����' in lr[metadatas[15]]:
                lr[metadatas[12]] = re.findall('����(.*?)��',lr[metadatas[15]],re.S)[0]
                lr[metadatas[13]] = re.findall('¥�㣺(.*?)��',lr[metadatas[15]],re.S)[0]
                lr[metadatas[14]] = _split(lr[metadatas[15]], '����', 1).split('װ�ޣ�')[0]
                lr[metadatas[29]] = _split(lr[metadatas[15]], 'װ�ޣ�', 1).split('�����')[0]
                lr[metadatas[9]] = _split(str_next_dl, '�����', 1).split('��')[0].strip()
            lr[metadatas[15]] = lr[metadatas[15]].split('¥��')[0]
        if '����' in lr[metadatas[15]]:
            lr[metadatas[15]] = lr[metadatas[15]].split('����')[0]
        if '���ϲ�����' in lr[metadatas[15]]:
            lr[metadatas[15]] = lr[metadatas[15]].split('���ϲ���')[0]
        try:
            if 'װ�ޣ�' in lr[metadatas[15]]:
                lr[metadatas[15]] = lr[metadatas[15]].split('װ��')[0]
        except:pass
        if '�������' in lr[metadatas[27]]:
            lr[metadatas[27]] = lr[metadatas[27]].split('�������')[0]
        if '��Ȩ����' in lr[metadatas[27]]:
            lr[metadatas[27]] = lr[metadatas[27]].split('��Ȩ���ʣ�')[0]
        if '�������' in lr[metadatas[14]]:
            lr[metadatas[14]] = lr[metadatas[14]].split('�������')[0]
        if 'С����' in lr[metadatas[14]]:
            lr[metadatas[14]] = lr[metadatas[14]].split('С����')[0]
        if '�����' in lr[metadatas[14]]:
            lr[metadatas[14]] = lr[metadatas[14]].split('�����')[0]
        if '¥�����ƣ�' in lr[metadatas[30]]:
            lr[metadatas[30]] = lr[metadatas[30]].split('¥�����ƣ�')[0]
        if 'С����' in lr[metadatas[29]]:
            lr[metadatas[29]] = lr[metadatas[29]].split('С����')[0]
        if '�����' in lr[metadatas[29]]:
            lr[metadatas[29]] = lr[metadatas[29]].split('�����')[0]
        try:
            if '�����������' in lr[metadatas[60]]:
                lr[metadatas[60]] = lr[metadatas[60]].split('�����������')[0]
        except:pass

        try:
            if '¥�����ƣ�' in lr[metadatas[60]]:
                lr[metadatas[60]] = lr[metadatas[60]].split('¥�����ƣ�')[0]
        except:pass

        lr[metadatas[6]] = _split(str_next_dl, '¥�����ƣ�', 1).split('(')[0].strip() \
                           or ''.join(s.strip() for s in re.findall('С����[^>]*>([^<]*)<', str(inforTxt_bs))) \
                           or _split(str_next_dl, '¥�����ƣ�', 1).replace("[��ͼ��ͨ]", '')

        try:
            lr[metadatas[3]] = _strip(city[3].string.replace('���ַ�', ''))
        except:
            lr[metadatas[3]] = ''
        lr[metadatas[48]] = _split(str_next_dl, '������ʩ��', 1).strip()
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
            lr[metadatas[8]] = _strip(xq_Bs.find('p').text.replace('��ַ��', ''))
        except Exception:
            lr[metadatas[8]] = ''
        try:
            lr[metadatas[47]] = _strip(xq_Bs.find('p').find_next('p').text.replace('��ͨ״����', ''))
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
            lr[metadatas[31]] = _strip(all_xq_dd[2].text.strip().replace('��ҵ���ͣ�', ''))
        except:
            lr[metadatas[31]] = ''
        try:
            lr[metadatas[49]] = _strip(all_xq_dd[3].text.strip().replace('�� �� �ʣ�', ''))
        except:
            lr[metadatas[49]] = ''
        try:
            lr[metadatas[51]] = _strip(all_xq_dd[4].text.strip().replace('�� ҵ �ѣ�', ''))
        except:
            lr[metadatas[51]] = ''
        try:
            lr[metadatas[50]] = _strip(all_xq_dd[5].text.strip().replace('��ҵ��˾��', ''))
        except:
            lr[metadatas[50]] = ''
        try:
            lr[metadatas[46]] = _strip(all_xq_dd[6].text.strip().replace('�� �� �̣�', ''))
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
        #����������Ϣд�����ݿ�
        # self.mysql.save(lr, metadatas)
        if lr[metadatas[1]].strip() == '':
            raise myException('���ݴ���,�����ֶ�Ϊ��!')
        self.completionlr(lr, metadatas)
        MySqlEx.save(lr, metadatas)
    #def getinfo(self, urlbase):
        #LOG.info('fang8getinfo���%s������ϸ��Ϣ' , urlbase.url)


if __name__ == '__main__':
    wfang = wwwfangcom()
    # print(len(wfang.default(UrlBase('http://esf.hz.fang.com/newsecond/esfcities.aspx', 'wwwfangcom',order='123'))))
    # wfang.getpages(UrlBean('http://esf.binzhou.fang.com/house/h316-i36-j3100/', 'wwwsfcom#getitem', param=10, headers='������',order='123'))
    # print(w58.getpages(UrlBean('http://bj.58.com/ershoufang/pn2', 'www58com#getitem', param=9, headers='����')))
    wfang.getitem(UrlBean('http://esf.sh.fang.com/chushou/3_247454960.htm', 'wwwfangcom#getitem', param='����',order='1234'))
    ls = (
'http://esf.tj.fang.com/chushou/3_191751219.htm',
'http://esf.sh.fang.com/chushou/3_245686871.htm',
'http://esf.sh.fang.com/chushou/3_245548373.htm',
'http://esf.hz.fang.com/chushou/3_178194568.htm',)
    for l in ls:
        wfang.getitem(UrlBean(l, 'wwwfangcom#getitem', param='����',order='1234'))