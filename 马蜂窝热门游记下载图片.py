from lxml import etree
import requests
from fake_useragent import UserAgent
import json
import re,os
ua = UserAgent()
headers = {'user-agent':ua.random}
from urllib.request import urlretrieve

#下载图片和找到seq值
def down_seq(url):
    html = requests.get(url,headers = headers)
    a = json.loads(html.text)#将html.text转化为字典类型的文本
    text = str(a)
    reg  = 'data-seq="(.*?)"'#提取seq值的正则表达式
    a = re.compile(reg).findall(text)#a = 最后一个seq值
    pic_url_reg = 'data-rt-src="(.*?)"' #提取图片url的正则表达式
    pic_url = re.compile(pic_url_reg).findall(text)
    
    for i in pic_url:
        n = hash(i)
        urlretrieve(i,path+r'//%s.jpg'%n)
        
    if a != []:
        a = a[-1]#a[-1]为需要的最后一个seq值
        return a

for i in range(1,2):#这里的数字指热门游记的页数
    url = 'http://pagelet.mafengwo.cn/note/pagelet/recommendNoteApi?&params={"type":0,"objid":0,"page":%s,"ajax":1,"retina":1}&_=1544587060673'%str(i)
    html = requests.get(url,headers = headers)
    text = json.loads(html.text)
    text = str(text)
    reg = '<a href="(/i/.*?.html)"'
    href = re.compile(reg).findall(text)#列表页抽取所有详情页的url
    href = set(href)
    for i in href:
        detail_url = 'http://www.mafengwo.cn'+i
        html = requests.get(detail_url,headers = headers)
        selector = etree.HTML(html.text)
        try:
            name = selector.xpath('//*[@id="_j_cover_box"]/div[3]/div[2]/div/h1/text()')#详情页的标题，将其作为存储图片的文件夹名字
            print(name[0])
            path = r'e://马蜂窝//%s'%name[0]
            if not os.path.exists(path):#创建文件夹
                    os.makedirs(path)
            #html = requests.get(detail_url,headers = headers)

            pic_url_reg = 'data-rt-src="(.*?)"' 
            pic_url = re.compile(pic_url_reg).findall(html.text)#提取第一分段的图片
            x = 1
            for i in pic_url:
                urlretrieve(i,path+r'//%s.jpg'%x)
                print(i)
                x += 1
            reg = 'data-seq="(.*?)"'
            seq = re.compile(reg).findall(html.text)
            seq = seq[-1]#第一分段最后一个seq值
            url = detail_url.split('/')
            url = url[-1]
            id = url.replace('.html','')#id号
            url = 'http://www.mafengwo.cn/note/ajax.php?act=getNoteDetailContentChunk&id=%s&seq=%s'%(id,seq)
            ulist = url.split('seq=')
            seq = down_seq(url)
            while True:
                url = ulist[0]+'seq='+str(seq)
                print('-= '*30)
                seq = down_seq(url)
                if seq == None:
                    break
        except IndexError:
                print('出错了')
                pass

