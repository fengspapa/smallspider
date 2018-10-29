import requests,re
from contextlib import closing

def getVideoName(url):
    html = requests.get(url).text
    title = re.findall('<title data-vue-meta="true">(.*?)_',html)[0]
    return title

#url = 'https://www.bilibili.com/video/av28348888/'   #把这里的链接改为你需要下载的视频链接
url = 'https://www.bilibili.com/video/av17267741'
html = requests.get(url=url).text
video_url = re.findall(r'"backup_url":\["(.*?)"',html)[0]
video_name = getVideoName(url)

with closing(requests.get(video_url, headers={'referer': url}, stream=True, verify=False)) as response:
    if response.status_code == 200:
        print('下载中......')
        with open(video_name + '.flv', 'wb') as file:
            for data in response.iter_content(chunk_size = 1024):
                file.write(data)
                file.flush()
            else:
                print('视频下载完毕！保存在此python程序同目录下！')



   
