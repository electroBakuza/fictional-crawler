import scrapy
from urlparse import urlparse
from urlparse import urljoin
import json as jsonParse

from scrapy_splash import SplashRequest

class JsonCrawler(scrapy.spiders.CrawlSpider):
	name = "JsonCrawler"		
	json = None
	filters = None
	with open('schema.json') as f:
		json = jsonParse.loads(f.read())	
	#-----------------------------#
	def start_requests(self):		
		self.filters =  self.parameter1 			
		#----load the json and get the object of filters	
		self.allowed_domains =  self.json[self.filters]['allowed_domains']  		
		self.start_urls =  self.json[self.filters]['start_urls'] 		
		self.custom_settings = {
			'DOWNLOAD_DELAY': 4,
			'CONCURRENT_REQUESTS_PER_IP': '8' ,
		}
		self.handle_httpstatus_list = self.json[self.filters]['handle_http_list'] #[403,404,301,302,303,307,308,503]
		print "------------------------------------------------------------------------------------------"
		pagination = "https://www.alibaba.com/catalog/mobile-phones_cid5090301?spm=a2700.galleryofferlist.pagination.1.52b535bc2UD2A7&page="		
		for page in range(0,10):
			yield SplashRequest(url= pagination+str(page), callback=self.parse, endpoint='render.html')
		#--------end of fetching----#
	#---parse function---#
	def parse(self, response):				
		
		headers= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
		try:
			response.meta['present_depth']
		except:
			response.meta['present_depth'] = 0
		try:
			response.meta['depth_limit']
		except:
			response.meta['depth_limit'] = self.json[self.filters]['depth_limit']	

		if response.meta['present_depth'] > response.meta['depth_limit']:
			return
		print '------------------------------------------------------------------------------------------'
		try:
			for newslink in response.css("a::attr(href)").extract():				
				try:
					if 	newslink.split('/')[3]!='en' and newslink.split('/')[2] == "www.urdupoint.com":
						continue
				except:
					continue		
				#avoid to scrap to third party website such like youtube
				if urlparse( response.url )[1] == urlparse( newslink )[1] :
					newslink=urljoin(response.url, newslink)
					yield SplashRequest(newslink, callback=self.extract, endpoint='render.html', headers=headers, meta={ 'present_depth': response.meta['present_depth']+1, 'depth_limit': response.meta['depth_limit']})
				else:
					continue
		except Exception as e:
			print e			
			pass
	#---end of parse function---#
	def extract(self, response):
		print "Extracting............................................................................................."
		if response.status == 200:			
			paths =   self.json[self.filters]['format']
			dict = {}
			dict['url'] = response.url
			dict['name'] =  self.filters
			for k, v in zip(paths.keys(), paths.values()):
				dict[ k ]  =  " ".join( response.css( v ).extract() )
			#----decide weather to save or not
			keys = self.json[self.filters]['save_check_on']	
			freq = 0
			for kValid in keys:
				if dict[kValid] == None or len(dict[kValid])<=0:
					freq+=1
			if freq==len(keys)+1:
				pass
			else:			
				print dict	 
				yield dict