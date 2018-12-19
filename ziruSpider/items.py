# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZiruspiderItem(scrapy.Item):
	# define the fields for your item here like:
	# name = scrapy.Field()
	title = scrapy.Field()
	addr = scrapy.Field()
	area = scrapy.Field()
	apartment = scrapy.Field()
	rooms = scrapy.Field()
	price = scrapy.Field()
