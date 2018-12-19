# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import redis
import random
from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message


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

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
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

    def __init__(self, ua):
        self.pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
        self.ua = ua

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        return cls(random.choice(crawler.settings.getlist("USER_AGENT")))

    def process_request(self, request, spider):
        con = redis.Redis(connection_pool=self.pool)
        proxy = con.srandmember("http_proxies", 1)[0].decode("utf-8")
        request.headers.setdefault("User-Agent", self.ua)
        request.meta["proxy"] = "http://" + proxy


class MyRetryMiddleware:

    def __init__(self, redis_setting):
        self.redis_con = redis.Redis(*redis_setting)

    @classmethod
    def from_crawler(cls, spider):
        return cls(spider.settings.getlist("REDIS"))

    def delete_and_change_proxy(self, proxy):
        if "https" in proxy:
            self.redis_con.srem("https_proxies", proxy[8:])
            return self.redis_con.srandmember("https_proxies", 1)[0].decode("utf-8")
        else:
            self.redis_con.srem("http_proxies", proxy[7:])
            return self.redis_con.srandmember("http_proxies", 1)[0].decode("utf-8")

    def process_exception(self, request, exception, spider):
        if exception:
            print(exception)
            request.meta['proxy'] = "https://" + self.delete_and_change_proxy(request.meta['proxy'])
            print("连接异常，更换代理ip重试", request.meta['proxy'])
            return request

    def process_response(self, request, response, spider):
        if response.status != 200:
            request.meta['proxy'] = "https://" + self.delete_and_change_proxy(request.meta['proxy'])
            print("状态码异常，更换代理ip重试", request.meta['proxy'])
            return request
        return response




