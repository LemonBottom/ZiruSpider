# -*- coding=utf-8 -*-
# Create ime:2018/10/30 11:09 AM
# Author:Chen

from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess

if __name__ == "__main__":
	proc = CrawlerProcess(get_project_settings())
	proc.crawl('hezuSpider')
	proc.start()