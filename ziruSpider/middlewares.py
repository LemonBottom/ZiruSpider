# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import redis
import random
import logging
from scrapy import signals, Request


class ZiruspiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ZiruspiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self, ua):
        self.ua = ua

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls(crawler.settings.get("USER_AGENT"))
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        request.headers['User-Agent'] = random.choice(self.ua)
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RandomProxy:
    """
    将每次请求加上代理ip
    """
    def __init__(self, proxy_key, redis_setting):
        self.proxy_key = proxy_key
        self.server = redis.Redis(*redis_setting)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get("PROXY_KEY"), crawler.settings.getlist("REDIS"))

    def set_proxy(self, server):
        return server.srandmember(self.proxy_key, 1)[0].decode("utf-8")

    def process_request(self, request, spider):
        request.meta["proxy"] = "http://" + self.set_proxy(self.server)

    def process_exception(self, request, exception, spider):
        if exception:
            logging.error("连接异常，返回消息队列")
            self.server.srem(self.proxy_key, request.meta['proxy'][7:])
            r = Request(request.url, callback=request.callback, dont_filter=True)
            try:
                r.meta['area_name'] = request.meta['area_name']
            except:
                pass
            return r

    def process_response(self, request, response, spider):
        if response.status != 200:
            logging.error("状态码异常，返回消息队列")
            self.server.srem(self.proxy_key, request.meta['proxy'][7:])
            r = Request(request.url, callback=request.callback, dont_filter=True)
            try:
                r.meta['area_name'] = request.meta['area_name']
            except:
                pass
            return r
        return response




