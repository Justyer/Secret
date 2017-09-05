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
             '����','����ͼƬ','γ��','����','str_order','������Դ')
import socket,time
#socket.timeout = 3
import requests, re
from bs4 import BeautifulSoup, Tag
from webparser.www_fang_com import wwwfangcom
class myException(Exception):pass
#�����ѷ���վ
class wwwfangcomSC(ParserBase):
    htmlwrite = HtmlFile()
    headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36 LBBROWSER', 'Connection': 'keep-alive'}
    shi = re.compile(r'(\d+)��|��|����')
    ting = re.compile(r'(\d+)��')
    wei = re.compile(r'(\d+)��')
    chu = re.compile(r'(\d+)��')
    yangtai = re.compile(r'(\d+)̨|��̨')

    pagenotfound = '��Դ�����ڣ�'

    def __init__(self):
        super(wwwfangcomSC, self).__init__()
    def default(self, urlbase):
        LOG.info('�ѷ�Ĭ�Ϸ�����ó����б�!')
        t = ('������','����','������','��������','����','����','����','����','����','����','��˳',
             '��Ϫ','����','����','�׳�','��ɫ','��ɽ','����','����','��ɽ','��ͷ','��Ӧ','����',
             '�����׶�','����','����','��������','����','����','��Ϫ','�Ͻ�','����','����','�ɽ',
             '����','����','����','����','����','����','����','����','����','����','����','����',
             '����','����','�е�','����','���','����','����','����','����','����','����','��Ϫ',
             '����','����','��Ϳ','����','��ͬ','���˰���','����','����','����','�º�','�»�','�Ƿ�',
             '����','����','����','�潭','����','����','����','����','����','��̨','��Ӫ','������˹',
             '��ƽ','��ʩ','����','����','�ʳ�','�ʶ�','����','���','�','���','����','����','����',
             '��˳','����','����','����','����','����','����','����','�߱���','����','����','����','�㰲',
             '����','��Ԫ','���','����','��ԭ','����','����','����','������','����','����','����','����',
             '����','����','����','Ԫ��','�ױ�','�ӳ�','�ϴ�','�׸�','�ں�','����','����','����','��Դ','����',
             '����','����','���','����','����','����','��Զ','�Ƹ�','����','��ɽ','�ݰ�','�ݶ�','��«��','���ױ���',
             '����','����','����','��ľ˹','����','����','����','����','����','����','����','������','����','��ī',
             '���','����','������','����','����','����','����','��̳','����','����','����','����','����','��Ȫ',
             '����','����','��Դ','����','����','��ƽ','����','����','��ƽ','��ʲ','��������','��������','����','����',
             '����','����','����','����','����','��ɽ','��ͤ','��ƽ','��ɽ','����','���Ƹ�','�ĳ�','����','��Դ','����',
             '����','����','�ٰ�','�ٲ�','�ٷ�','�ٺ�','����','����','����','����','���','��֥','��ˮ','����ˮ','���',
             '����','����','����','����','����','¤��','����','¦��','����','����','����','®��','���','����','����',
             '����','����ɽ','ï��','üɽ','÷��','�Ͻ�','����','ĵ����','�ϰ�','�ϳ�','��ƽ','����','����','�ڽ�','����',
             '����','����','ũ��','ŭ��','�̽�','��֦��','����','����','����','ƽ��ɽ','ƽ��','ƽ��','ƽ��','ƽ̶','Ƽ��',
             'ƽ��','����','�ն�','������','����','���','Ǩ��','ǭ����','ǭ��','Ǳ��','ǭ��','Ǩ��','ǭ����','����','�뽭',
             '����','����','��Զ','����','����','����','�������','��̨��','����','����','�տ���','����','�ٲ�','�綫','���',
             '��','���','����','����Ͽ','����','��ɳ','�̺�','����','����','����','����','��־','ɽ��','��ͷ','��β','�ع�',
             '����','����','��ũ��','ʯʨ','ʮ��','ʯ��','ʯ��ɽ','�ٹ�','˫Ѽɽ','˳��','˷��','����','��ƽ','����','��ԭ',
             '�绯','���','����','��Ǩ','����','̩��','̫��','̨ɽ','̩��','̨��','����','����','��ˮ','����','ͩ��','ͭ��',
             'ͨ��','ͨ��','ͭ��','ͩ®','����','ͭ��','ͩ��','��³��','ͼľ���','�߷���','����','μ��','�İ�','����','��ɽ',
             '�����첼','�峣','�ں�','���','�ߺ�','�޼�','�⽭','�����','��¡','����','��ָɽ','����','����','��ɽ','����',
             '����','����','����','����','Т��','�°�','�˰���','�˻�','��̨','����','����','�½�','����','���ֹ�����','����',
             '����','��̩','����','����','����','����','��֣','����','��˫����','����','����','����','�Ű�','�Ӱ�','�ӱ�',
             '�γ�','����','����','��Ȫ','۳��','��ʦ','�˱�','����','�˴�','�˶�','����','Ӫ��','ӥ̶','����','����','����',
             '����','����','����','����','����','����','����','����','��','����','�˳�','�Ƹ�','����','����','����','����',
             '��Ϫ','��Ҧ','����','����','��ׯ','�ű�','�żҸ�','�żҽ�','�żҿ�','����','��Ҵ','տ��','�ض�','����','��ͨ',
             '����','��Զ','��Դ','����','��','֦��','��Ĳ','����','����','�ܿ�','��ɽ','����','ׯ��','���','����','פ����',
             '����','�Ͳ�','�Թ�','����','�޳�','��ƽ','��','����',
             '�����','����','��üɽ','��ɽ','��ϼ','��ɽ','�䰲','����',
             '����','��ɽ','�ﴨ','����','������','����','��ɽ','���','����',
             '����','����','����','����','ͭ��','���','����','����','����','����',
             '�ߴ�','����','����','����','��','��̩','����','�ᶼ','����','����',
             '����','ͭɽ','����','����','����','̨��','����','��Դ','������','Ȫɽ',
             '����','ƽɽ','����','����','����','����','����','���','����','�½�',
             '����','����','����','���ֺ���','����','Ȫ��')

        r = requests.get(urlbase.url, headers=self.headers, timeout=(3.05, 3.5))
        LOG.info('���ʺ�ʱ:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwfangcomSC %s ����״̬:%s', urlbase.url, r.status_code)
            return None
        soup = BeautifulSoup(r.content.decode('gbk', errors='ignore'), 'html.parser') #lxml
        citys = soup.find('div', id='c01').find_all('a')
        ls = []
        i_order = urlbase.order+'0'
        #���Ӳɼ���4ҳ
        for i in citys:
            if i.text in t or not wwwfangcom.hasCity(i.text):
                for i_oth in range(1, 5):
                    ls.append(UrlBean(i['href']+('/esfhouse/h3%d/' % i_oth), self.message('getpages'), param=i_oth, headers=i.text, order=i_order))
                    LOG.info('��ó���%sҳ����Ϣ%s', i.text, i['href']+('/esfhouse/h3%d/' % i_oth))
        return ls

    #�������ж��ַ��б�ҳ
    def getpages(self, urlbase):
        LOG.info('fangSCgetpages��ó���%s���ַ��б���Ϣ', urlbase.url)
        r = requests.get(urlbase.url, headers=self.headers, timeout=(3.05, 3.5))
        LOG.info('���ʺ�ʱ:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwfangcomSC %s ����״̬:%s', urlbase.url, r.status_code)
            return None
        soup = BeautifulSoup(r.content.decode('gbk', errors='ignore'), 'html.parser') #lxml
        #û���ҵ���Ϣ�ͷ��ؿ�
        try:
            items = soup.find('div',attrs={'class':'houseList'}).find_all('a')
        except:
            return []
        ls = []
        host = '/'.join(r.url.split('/')[:3])
        itemIndex = 1
        i_order = urlbase.order+'1'
        for item in items:
            try:
                if item.text !='' and item.text !='\n' and '/cs/' in item['href'] and item['title'] != '�ö���Դ' :
                    strUrl = item['href'] if 'http' in item['href'].lower() else host+item['href']
                    ls.append(UrlBean(strUrl, self.message('getitem'), key=strUrl, param=urlbase.headers, order=i_order))
                    LOG.debug('%s��%dҳ%d��' % (urlbase.headers, urlbase.param, itemIndex))
                    itemIndex += 1
            except Exception as e:
                continue
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
    def getitem(self, urlbase):
        LOG.info('fangSCgetinfo��ó���%s������ϸ��Ϣ', urlbase.url)
        r = requests.get(urlbase.url, headers=self.headers, timeout=(3.05, 3.5))
        LOG.info('���ʺ�ʱ:%.4f, url:%s', r.elapsed.microseconds/1000000, r.url)
        self.htmlwrite.save('%s\\%s\\%s' %(self.__class__.__name__, '���ַ�', urlbase.param), r.url, r.text)
        if(r.status_code != requests.codes.ok):
            LOG.warning('wwwfangcomSC %s ����״̬:%s', urlbase.url, r.status_code)
            return
        reText = r.text
        soup = BeautifulSoup(r.content.decode('gbk', errors='ignore'), 'html.parser') #lxml
        #������ص��Ƿ�Դ������ҳ���ֱ���˳�
        try:
            if self.pagenotfound in soup.getText(strip=True):
                LOG.info('url:%s %s', urlbase.url, self.pagenotfound)
                return
        except:pass
        lr = {}
        ###############################################
        def _split(str_all, str, index):
            try:
                return _strip(str_all).split(str)[index]
            except Exception:
                return ''

        def _strip(str_info):
            return str_info.strip().replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '')

        title1 = soup.find('h2',attrs={'class':'title clearfix'}).find_all('span',attrs={'class':'txt floatl'})
        for title2 in title1:
            lr[metadatas[5]] = title2.text.strip()

        lr[metadatas[4]] = urlbase.url
        try:
            xq_name = re.findall('С<span class="pl27"></span>����</span><strong style="font-size: 14px;">(.*?)</strong>',reText,re.S) \
                      or re.findall('С ����</span><strong style="font-size: 14px;">(.*?)</strong>',reText,re.S) \
                      or [re.findall('С ����</span>((?!<strong).)*<strong[^>]*>([^<]*)</strong>',reText,re.S)[0][1]]
            dr = re.compile(r'<[^>]+>',re.S)
            lr[metadatas[6]] = dr.sub('',xq_name[0]).strip()
        except:
            lr[metadatas[6]] =''

        try:
            area = re.findall('id="detail05">(.*?)<',reText,re.S)
            lr[metadatas[3]] =area[0].replace('���ַ�','').strip()
        except:
            lr[metadatas[3]] =''



        ld_name = soup.find('div',attrs={'class':'bread'}).find_all('a')
        try:
            lr[metadatas[61]] = (">".join([_strip(dd.text) for dd in ld_name])).replace('���ַ�', '').strip()
        except:
            lr[metadatas[61]] =''

        try:
            year = re.findall('��<span class="pl27"></span>����</span><strong style="font-size: 14px;">(.*?)</strong>',reText,re.S)
            lr[metadatas[9]] = year[0]
        except:
            lr[metadatas[9]] =''

        try:
            floor = (re.findall('</span>�㣺</span>(.*?)</dd>',reText,re.S) \
                     or [str(soup.find('span', text=re.compile('¥\s*�㣺?')).nextSibling)])[0]
            lr[metadatas[11]] = floor.strip()
        except:
            lr[metadatas[11]] = ''

        try:
            z_floor = re.findall('\(��(.*?)��',reText,re.S)
            lr[metadatas[12]]= z_floor[0]
        except:
            lr[metadatas[12]] =''

        try:
            dq_floor = re.findall('�㣺</span>��(.*?)��',reText,re.S)
            lr[metadatas[13]] = dq_floor[0]
        except:
            lr[metadatas[13]] =''

        try:
            toward = re.findall('��</span>(.*?)<',reText,re.S)
            lr[metadatas[14]] = toward[0]
        except:
            lr[metadatas[14]] =''

        try:
            jz_area = re.findall('���������</span>(.*?)O',reText,re.S)
            lr[metadatas[15]] = re.search(r"\d+\.?\d*",jz_area[0].strip()).group()
            if lr[metadatas[15]] is None:
                lr[metadatas[15]] =''
        except:
            lr[metadatas[15]] =''

        try:
            cqxz = re.findall('��Ȩ���ʣ�</span>(.*?)<',reText,re.S)
            lr[metadatas[28]] = cqxz[0]
        except:
            lr[metadatas[28]] =''

        try:
            decorate = re.findall('�ޣ�</span>(.*?)<',reText,re.S)
            lr[metadatas[29]] = decorate[0]
        except:
            lr[metadatas[29]] =''

        try:
            house = re.findall('�� �ͣ�</span>(.*?)</dd>',reText,re.S)
            house_t= house[0]
            lr[metadatas[17]] =house_t
        except:
            lr[metadatas[17]] =''
        try:
            lr[metadatas[18]] = re.search(wwwfangcomSC.shi,lr[metadatas[17]]).group(1)
        except:
            lr[metadatas[18]] = ''
        try:
            lr[metadatas[19]] = re.search(wwwfangcomSC.ting,lr[metadatas[17]]).group(1)
        except:
            lr[metadatas[19]] = ''
        try:
            lr[metadatas[20]] = re.search(wwwfangcomSC.wei,lr[metadatas[17]]).group(1)
        except:
            lr[metadatas[20]] = ''
        try:
            lr[metadatas[21]] = re.search(wwwfangcomSC.chu,lr[metadatas[17]]).group(1)
        except:
            lr[metadatas[21]] = ''
        try:
            lr[metadatas[22]] = re.search(wwwfangcomSC.yangtai,lr[metadatas[17]]).group(1)
        except:
            lr[metadatas[22]] = ''
        try:
            u_price = re.findall('</span>��\��(.*?)Ԫ',reText,re.S)
            lr[metadatas[24]] = u_price[0].replace('O', '').replace('�O','')
        except:
            lr[metadatas[24]] =''

        try:
            t_price = re.findall('</span><span class="num30">(.*?)<',reText,re.S)
            lr[metadatas[23]] = t_price[0]
        except:
            lr[metadatas[23]] =''
        try:
            lxr_name = re.findall('<strong class="black">(.*?)</span>',reText,re.S) \
                       or re.findall('<span class="name floatl">(.*?)<span class="org">',reText,re.S)
            if len(lxr_name)==0:
                try:
                    lxr_name = [soup.find('div', class_='agentInf').find('p', class_='namer').getText(strip=True)]
                except:pass
            dr = re.compile(r'<[^>]+>',re.S)
            lr[metadatas[33]] = dr.sub('',lxr_name[0]).replace(' ','').strip()
        except:
            lr[metadatas[33]] =''

        try:
            if soup.find('span',class_='Span3'):
                lr[metadatas[34]] = soup.find('span',class_='Span3').find('a')['href']
            elif soup.find('p',class_='checkshop'):
                lr[metadatas[34]] = soup.find('p',class_='checkshop').find('a')['href']
            else:
                lr[metadatas[34]] = ''
        except:
            lr[metadatas[34]] = ''


        try:
            telephone = re.findall('<input type="hidden" value="(.*?)"',reText,re.S)
            lr[metadatas[37]] = telephone[0]
        except:
            lr[metadatas[37]] =''

        try:
            fybh = re.findall('��Դ��ţ�(.*?)<span class="pl25">',reText,re.S)[0]
            lr[metadatas[40]] = _strip(fybh).replace('&nbsp;','')
        except:
            lr[metadatas[40]] =''

        try:
            fb_time = re.findall('����ʱ�䣺(.*?)<',reText,re.S)[0]
            t_time = time.strptime(fb_time.split('(')[0].replace('/','-'), "%Y-%m-%d %H:%M:%S")
            lr[metadatas[41]] = time.strftime("%Y-%m-%d %H:%M:%S",t_time)
        except Exception as e:
            lr[metadatas[41]] =''

        try:
            zz_category = re.findall('סլ���ͣ�</span>(.*?)<',reText,re.S)
            lr[metadatas[27]] = zz_category[0]
        except:
            lr[metadatas[27]] =''

        try:
            jz_category = re.findall('�������ͣ�</span>(.*?)<',reText,re.S)
            lr[metadatas[30]] = jz_category[0]
        except:
            lr[metadatas[30]] =''

        try:
            facilities = re.findall('������ʩ��</span>(.*?)<',reText,re.S) or re.findall('<span class="bluebtn" id="detail17">(.*?)</span>',reText,re.S)
            lr[metadatas[48]] = facilities[0].strip().replace('<div>','').replace('</div>','')
        except:
            lr[metadatas[48]] =''

        try:
            facilities = re.findall('��ҵ���ͣ�</span>(.*?)<',reText,re.S)
            lr[metadatas[31]] = facilities[0]
        except:
            lr[metadatas[31]] =''

        try:
            xqjj = re.findall('С����飺</span>(.*?)</dt>',reText,re.S)[0]
            dr = re.compile(r'<[^>]+>',re.S)
            lr[metadatas[32]] = _strip(re.sub(dr,'',xqjj))[0:2000]
        except:
            lr[metadatas[32]] = ''
        try:
            kfs = re.findall('��</span>�̣�</span>(.*?)</dd>',reText,re.S)[0]
            lr[metadatas[46]] = _strip(kfs)
        except:
            lr[metadatas[46]] = ''

        try:
            greening = re.findall('�ʣ�</span>(.*?)<',reText,re.S)
            lr[metadatas[49]] = greening[0]
        except:
            lr[metadatas[49]] =''

        try:
            wygs = re.findall('��ҵ��˾��</span>(.*?)</dd>',reText,re.S)[0]
            lr[metadatas[50]] = _strip(wygs)
        except:
            lr[metadatas[50]] = ''

        try:
            costs = re.findall('�ѣ�</span>(.*?)<',reText,re.S)
            lr[metadatas[51]] = costs[0]
        except:
            lr[metadatas[51]] =''

        try:
            city = re.findall('name="city" value="(.*?)"',reText,re.S)
            lr[metadatas[1]] =city[0]
        except:
            lr[metadatas[1]] =''

        xz_area = soup.find('div',attrs={'class':'bread'}).find_all('a',id='detail03')
        try:
            for xz_area1 in xz_area:
                lr[metadatas[2]] =xz_area1.text.strip()
        except:
             lr[metadatas[2]] =''
        try:
            lr[metadatas[8]] = soup.find('div', class_='info rel floatr').find('span', text=re.compile('�� ַ��')).parent.getText(strip=True).replace('�� ַ��', '')
        except:
            lr[metadatas[8]] = ''

        lr[metadatas[0]] = 's00000sf'
        lr[metadatas[66]] = 'sf'

        lr[metadatas[65]] = urlbase.order if urlbase.order is not None else ''

        lr[metadatas[7]] = ''
        lr[metadatas[10]] = ''
        lr[metadatas[16]] =''
        lr[metadatas[25]] = ''
        lr[metadatas[26]] = ''
        lr[metadatas[35]] = ''
        lr[metadatas[36]] = ''
        lr[metadatas[38]] = ''
        lr[metadatas[39]] = ''
        lr[metadatas[42]] = ''
        lr[metadatas[43]] = ''
        lr[metadatas[44]] = ''
        lr[metadatas[45]] = ''
        lr[metadatas[47]] = ''
        lr[metadatas[52]] = ''
        lr[metadatas[53]] = ''
        lr[metadatas[54]] = ''
        lr[metadatas[55]] = ''
        lr[metadatas[56]] = ''
        lr[metadatas[57]] = ''
        lr[metadatas[58]] = ''
        lr[metadatas[59]] = ''
        lr[metadatas[60]] = ''
        lr[metadatas[62]] = ''
        lr[metadatas[63]] = ''
        lr[metadatas[64]] = ''
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
        self.completionlr(lr, metadatas)
        MySqlEx.save(lr, metadatas)
    #def getinfo(self, urlbase):
        #LOG.info('fang8getinfo���%s������ϸ��Ϣ' , urlbase.url)


if __name__ == '__main__':
    wfang = wwwfangcomSC()
    # print(len(wfang.default(UrlBase('http://esf.fang.com/newsecond/esfcities.aspx', 'wwwsjcomSZ',order='123'))))
    # wfang.getpages(UrlBean('http://esf.yangqu.fang.com/esfhouse/h31/', 'wwwsfcom#getitem', param=10, headers='������',order='123'))
    # wfang.getitem(UrlBean('http://esf.yangchun.fang.com/cs/20415.htm', 'wwwsfcomSC#getitem', param=9, headers='������',order='123456'))
    # wfang.getitem(UrlBean('http://esf.xishuangbanna.fang.com/cs/98518.htm', 'wwwfangcomSC#getitem', param='����',order='1234'))
    wfang.getitem(UrlBean('http://esf.cangzhou.fang.com/cs/3_153041228.htm', 'wwwfangcomSC#getitem', param='����',order='1234'))
    ls = ('http://esf.ahsuzhou.fang.com/cs/94013.htm',
          'http://esf.ahcf.fang.com/cs/800.htm',
          'http://esf.ankang.fang.com/cs/3_150449315.htm',
          'http://esf.guangrao.fang.com/cs/2744.htm',
          'http://esf.guangrao.fang.com/cs/2749.htm',
          'http://esf.jiaonan.fang.com/cs/21976.htm',
          'http://esf.puer.fang.com/cs/122278.htm',
          'http://esf.guangrao.fang.com/cs/2763.htm',
          'http://esf.sdcl.fang.com/cs/4122.htm',
          'http://esf.yangchun.fang.com/cs/24687.htm')

    for l in ls:
        wfang.getitem(UrlBean(l, 'wwwfangcom#getitem', param='����',order='1234'))