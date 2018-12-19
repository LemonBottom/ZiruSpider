# -*- coding: utf-8 -*-
import scrapy
import re
import requests
from ziruSpider.items import ZiruspiderItem
from scrapy import Request
from .ocrBaidu import OcrBaidu


class HezuspiderSpider(scrapy.spiders.CrawlSpider):
	name = 'hezuSpider'
	allowed_domains = ['ziroom.com']
	start_urls = ['http://www.ziroom.com/z/nl/z2.html?qwd=&p=1/']

	def parse(self, response):
		# 获取"区域"的a标签
		area_a_list = response.xpath("//dl[@class='clearfix zIndex6']/dd/ul/li/span/a")
		for area_a in area_a_list:
			# "区域"的url
			url = "http:" + area_a.xpath("./@href").extract_first()
			# "区域"名称
			area_name = area_a.xpath("./text()").extract_first()
			request = Request(url, callback=self.single_page_parse)
			request.meta['area_name'] = area_name
			yield request

	def single_page_parse(self, response):
		ul = response.xpath("//ul[@id='houseList']/li[not(contains(@class,'zry'))]")
		# 获取价格列表
		try:
			price_list = self.price_list(response)
		except IndexError:
			# 如果status_code=200但是页面获取不完全，重新发送相同request
			request_partial = response.request
			request_partial.dont_filter = True
			yield request_partial
		# 迭代获得每个房间的信息
		for i, li in enumerate(ul):
			title = li.xpath("./div[@class='txt']/h3/a[@class='t1']/text()").extract()[0]
			detail_list = li.xpath("./div[@class='txt']/div[@class='detail']/p/span/text()").extract()
			area = response.meta['area_name']
			addr = detail_list[0]
			apartment = detail_list[1]
			rooms = detail_list[2]
			price = price_list[i]
			# print(title,area,addr,apartment,rooms,price)
			item = ZiruspiderItem(title=title, area=area, addr=addr, apartment=apartment, rooms=rooms, price=price)
			yield item
		url = response.xpath("//div[@class='pages']/a[@class='next']/@href").extract_first()
		if url:
			request = Request('http:' + url, callback=self.single_page_parse)
			request.meta['area_name'] = response.meta['area_name']
			yield request

	def price_list(self, response):
		"""
		返回每页18个价格列表
		:param response:
		:return:
		"""
		# 获取图片
		price_url = re.compile('image":"(\S+\.png)",').findall(response.body.decode("utf-8"))[0]
		while True:
			try:
				image_r = requests.get('http:' + price_url)
				image_r.raise_for_status()
				image_r.encoding = image_r.apparent_encoding
				image_bin = image_r.content
				break
			except:
				print("图片获取失败,重新尝试")
		# 先使用低精度识别
		while True:
			try:
				words = OcrBaidu().ocr(image_bin, "low")
				if len(words) < 10:
					# 图片分析少于十个数字时调用高精度识别orc
					words = OcrBaidu().ocr(image_bin, "high")
				print(words)
				break
			except:
				pass
		# 抓取价格偏移量
		price_18_list = eval(re.compile('offset":(\S+)};').findall(response.body.decode("utf-8"))[0])
		price_list = []
		for i in price_18_list:
			s = ''
			for x in i:
				s += words[int(x)]
			price_list.append(s)
		return price_list


