import requests
from lxml import etree
from fake_useragent import UserAgent
import random
from queue import Queue
import threading
ua = UserAgent()
from pymysql import *
headers = {'user-agent':ua.random}
proxies = [
{'http':'http://117.191.11.74:80'},
{'http':'http://117.191.11.112:80'},
{'http':'http://39.137.168.230:8080'},
{'http':'http://27.203.242.49:8060'},
{'http':'http://117.191.11.101:80'},
{'http':'http://222.89.85.158:8060'},
{'http':'http://117.191.11.111:80'},
{'http':'http://140.143.142.218:1080'},
{'http':'http://109.164.113.232:53281'},
{'http':'http://37.220.78.138:52288'},
{'http':'http://185.89.90.46:47640'},
{'http':'http://54.36.9.176:1080'},
{'http':'http://94.130.189.68:3128'},
{'http':'http://91.203.114.22:50068'},
{'http':'http://222.89.85.158:8060'},
{'http':'http://101.4.136.34:81'},
{'http':'http://78.26.207.173:53281'},
{'http':'http://176.53.2.122:8080'},
{'http':'http://82.193.123.230:53281'},
{'http':'http://109.197.190.34:53281'},
{'http':'http://190.8.168.252:8080'},
]

class Procuder(threading.Thread):
	def __init__(self,url_queue,sql_queue,*args,**kwargs):
		super(Procuder,self).__init__(*args,**kwargs)
		self.headers = {'user-agent':ua.random}
		self.url_queue = url_queue
		self.sql_queue =sql_queue

	def run(self):
		while True:
			if self.url_queue.empty():
				break
			queueLock.acquire()
			xq = self.url_queue.get()#详情页出队
			queueLock.release()
			self.two(xq)

	def two(self,url):
		html = requests.get(url,headers = self.headers,proxies = random.choice(proxies))
		response = etree.HTML(html.text)
		work_year = response.xpath('//*[@id="main"]/div[1]/div/div/div[2]/div[1]/span/text()')#发布时间
		job_name = response.xpath('//*[@id="main"]/div[1]/div/div/div[2]/div[2]/h1/text()')#职位名称
		money = response.xpath('//*[@id="main"]/div[1]/div/div/div[2]/div[2]/span/text()')#薪水
		money = str(money)
		money = money.replace('[','').replace(']','').replace(r'\n ','').replace('  ','').replace("'",'').replace(',','')
		city = response.xpath('//*[@id="main"]/div[1]/div/div/div[2]/p/text()[1]')#工作地点
		experience = response.xpath('//*[@id="main"]/div[1]/div/div/div[2]/p/text()[2]')#经验
		education = response.xpath('//*[@id="main"]/div[1]/div/div/div[2]/p/text()[3]')#学历
		company = response.xpath('//*[@id="main"]/div[1]/div/div/div[3]/h3/a/text()')#公司
		listing = response.xpath('//*[@id="main"]/div[1]/div/div/div[3]/p[1]/text()[1]')#融资情况
		number = response.xpath('//*[@id="main"]/div[1]/div/div/div[3]/p[1]/text()[2]')#公司人数
		company_href = response.xpath('//*[@id="main"]/div[1]/div/div/div[3]/p[2]/text()')#公司链接
		content = response.xpath('//*[@id="main"]/div[3]/div/div[2]/div[3]/div[1]/div/text()')
		content = str(content)
		content = content.replace('[','').replace(']','').replace(r'\n ','').replace('  ','').replace("'",'').replace(',','')#工作详情
		company_content = response.xpath('//*[@id="main"]/div[3]/div/div[2]/div[3]/div[2]/div/text()')
		company_content = str(company_content)
		company_content = company_content.replace('[','').replace(']','').replace(r'\n ','').replace(' ','').replace("'",'').replace(',','')

		work_year,job_name,money,city,experience,education,company,listing,number,company_href,content,company_content = str(work_year),str(job_name),str(money),str(city),str(experience),str(education),str(company),str(listing),str(number),str(company_href),str(content),str(company_content)
		work_year = work_year.replace("['",'').replace("']",'')
		job_name = job_name.replace("['",'').replace("']",'')
		money = money.replace("['",'').replace("']",'')
		city = city.replace("['",'').replace("']",'')
		experience = experience.replace("['",'').replace("']",'')
		education = education.replace("['",'').replace("']",'')
		company = company.replace("['",'').replace("']",'')
		listing = listing.replace("['",'').replace("']",'')
		number = number.replace("['",'').replace("']",'')
		company_href = company_href.replace("['",'').replace("']",'')
		content = content.replace("['",'').replace("']",'').replace('\\','')
		company_content = company_content.replace("['",'').replace("']",'').replace('\\','').replace('"','')
		#sql = '''insert into book_booktest(id,work_year,job_name,money,city,experience,education,company,listing,number,company_href,content,company_content) values (0,"%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s");''' %(work_year,job_name,money,city,experience,education,company,listing,number,company_href,content,company_content)
		#print(work_year,job_name,money,city,experience,education,company,listing,number,company_href,content,company_content)
		queueLock.acquire()
		self.sql_queue.put((work_year,job_name,money,city,experience,education,company,listing,number,company_href,content,company_content))#数据入队
		#print(self.sql_queue.qsize())
		queueLock.release()

class Consumer(threading.Thread):
	def __init__(self,url_queue,sql_queue,*args,**kwargs):
		super(Consumer,self).__init__(*args,**kwargs)
		self.url_queue = url_queue
		self.sql_queue = sql_queue
		self.connect = connect(host='localhost',user='root', password='mima', port=3306,db = 'spiders', charset='utf8')
		self.cursor = self.connect.cursor()
	def __del__(self):
		self.cursor.close()
		self.connect.close()
	def run(self):
		while True:
			if self.sql_queue.empty():
				break
			queueLock.acquire()
			
			work_year,job_name,money,city,experience,education,company,listing,number,company_href,content,company_content = self.sql_queue.get()#数据出队			
			sql = '''insert into book_booktest(id,work_year,job_name,money,city,experience,education,company,listing,number,company_href,content,company_content) values (0,"{}","{}","{}","{}","{}","{}","{}","{}","{}","{}",'{}',"{}");'''.format(work_year,job_name,money,city,experience,education,company,listing,number,company_href,content,company_content)
			#sql语句
			print(sql)
			self.cursor.execute(sql)#执行sql语句
			self.connect.commit()
			queueLock.release()

def run():
	url_queue = Queue(1000)
	
	sql_queue = Queue(1000)
	for i in range(1,40):
		url = 'https://www.zhipin.com/c101280100/?query=python&page='+str(i)
		html = requests.get(url,headers = headers,proxies =random.choice(proxies))
		selector = etree.HTML(html.text)
		next = selector.xpath('//*[@class="page"]/a[last()]/@href')
		next = str(next)
		next = next.replace("['",'').replace("']",'')
		if next != 'javascript:;':
			li_list = selector.xpath('//*[@id="main"]/div/div[2]/ul/li/div/div/h3/a/@href')
			for l in li_list:
				l = 'https://www.zhipin.com'+l
				url_queue.put(l)#url入队
				
		else:
			li_list = selector.xpath('//*[@id="main"]/div/div[2]/ul/li/div/div/h3/a/@href')
			for l in li_list:
				l = 'https://www.zhipin.com'+l
				url_queue.put(l)
				
			break
	for i in range(10):
		t = Procuder(url_queue,sql_queue)
		t.start()

	for i in range(10):
		t = Consumer(url_queue,sql_queue)
		t.start()

	

if __name__ == '__main__':
	queueLock = threading.Lock()
	run()