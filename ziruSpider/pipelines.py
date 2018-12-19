# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb


class ZiruspiderPipeline(object):

	def open_spider(self, spider):
		self.con = MySQLdb.connect(host="127.0.0.1", port=3306, user='root', passwd='123', db='ziru', charset='utf8')
		self.cur = self.con.cursor()
		self.con.autocommit(1)

	def process_item(self, item, spider):
		self.cur.execute(
			f"insert into zufang values (null,'{item['title']}','{item['area']}','{item['addr']}','{item['apartment']}','{item['rooms']}',{item['price']});"
		)
		return item

	def close_spider(self, spider):
		self.con.close()
