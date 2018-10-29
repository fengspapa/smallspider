import requests
import re
import os
import urllib.request
import time
url = 'http://hhzapi.ishuhui.com/cartoon/post/ver/76906890/id/10922.json'

def bao(url):
    html = requests.get(url)
    global befor
    befor = html.json()['data']['prev']['id']
    title = html.json()['data']['title']
    number = html.json()['data']['number']
    book_name = html.json()['data']['book_text']
    id = html.json()['data']['id']
    path = 'e:/漫画/%s/%s话 %s/' % (book_name,number, title)
    if not os.path.exists(path):
        os.makedirs(path)
    a = html.json()['data']['content_img']
    a = a.replace('/upload','').replace('{','').replace('}','')
    reg = '/cartoon/book.*?.g'
    c = re.compile(reg).findall(a)
    x = 1
    for i in c:
        i = 'http://pic04.ishuhui.com' + i

        paths = path + '%s.jpg' % x

        if os.path.exists(paths) == True:
            print('%s话%s.jpg已存在' % (number, x))
            pass
        else:
            urllib.request.urlretrieve(i, paths)
        x += 1
bao(url)
for i in range(300):
    url2 = 'http://hhzapi.ishuhui.com/cartoon/post/ver/76906890/id/' + str(befor) + '.json'
    bao(url2)
    time.sleep(0.5)





