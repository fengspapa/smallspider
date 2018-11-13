import requests,time,os,re
from lxml import etree
from urllib import request
from fake_useragent import UserAgent
ua = UserAgent()
import threading
from queue import Queue


class Procuder(threading.Thread):
	headers = {'user-agent':ua.random}

	def __init__(self,page_queue,img_queue,*args,**kwargs):
		super(Procuder,self).__init__(*args,**kwargs)
		self.page_queue = page_queue
		self.img_queue = img_queue

	def run(self):
		while True:
			if self.page_queue.empty():
				break
			url = self.page_queue.get()#将页面url从队列中拿出
			self.parse(url)

	def parse(self,url):
		html = requests.get(url,headers = self.headers)
		selector = etree.HTML(html.text)
		tu = selector.xpath('//div[@class="page-content text-center"]//img[@class!="gif"]') 
		for t in tu:
			img_url = t.get('data-original')
			img_url = str(img_url)
			img_url = img_url.replace('!dta','')
			name = t.get('alt')
			name = re.sub(r'[\?？\.,，。]','',name)
			suffit = os.path.splitext(img_url)[1]

			filename = name+suffit
			self.img_queue.put((img_url,filename))#将img_url,filename传到队列里
			#

class Consumer(threading.Thread):
	def __init__(self,page_queue,img_queue,*args,**kwargs):
		super(Consumer,self).__init__(*args,**kwargs)
		self.page_queue = page_queue
		self.img_queue = img_queue

	def run(self):
		while True:
			if self.img_queue.empty() and self.page_queue.empty():#当2个队列都为空时，停止线程
				break
			img_url,filename = self.img_queue.get()#将img_url,filename从队列拿出
			request.urlretrieve(img_url,'image/%s'%filename)
			print(filename,'下载完成')

def run():
	page_queue = Queue(100)#创建页面队列
	img_queue = Queue(2000)#创建图片href队列
	for i in range(1,100):
		url = 'https://www.doutula.com/photo/list/?page='+str(i)
		page_queue.put(url)#将100个url加入页面队列
	for i in range(50):
		t = Procuder(page_queue,img_queue)
		t.start()

	for i in range(50):
		t1 = Consumer(page_queue,img_queue)
		t1.start()

if __name__ == '__main__':
	run()





	
