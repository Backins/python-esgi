# -*- coding: utf-8 -*-
import scrapy
from twisted.internet import reactor
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.http import Request, HtmlResponse
from urllib.parse import urlparse
from queue import Queue
from multiprocessing import Process

class ScrapResultItem(scrapy.Item):
    url = scrapy.Field()


class WebSpider(scrapy.Spider):
    name = 'webcrawler'

    def __init__(self, **kw):
        super(WebSpider, self).__init__(**kw)

        url = kw.get('target')
        queue = kw.get('queue')

        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'http://%s/' % url

        self.url = url
        self.allowed_domains = [urlparse(url).hostname]
        self.link_extractor = LinkExtractor()

    def start_requests(self):
        return [Request(self.url, callback=self.parse, dont_filter=True)]

    def parse(self, response):
        page = ScrapResultItem(url=response.url)

        if self.callback and callable(self.callback):
            self.callback(response)


        r = [page]
        r.extend(self._extract_requests(response))
        return r

    def _extract_requests(self, response):
        r = []
        if isinstance(response, HtmlResponse):
            links = self.link_extractor.extract_links(response)
            r.extend(Request(x.url, callback=self.parse) for x in links)
        return r

   def launch_crawler(target, callback):
    process_queue = Queue()

    def process(target, callback):
        try:
            process = CrawlerRunner({
                'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
                'CLOSESPIDER_ITEMCOUNT': 10
            })

            d = process.crawl(WebSpider, target=target, callback=proces)
            d.addBoth(lambda _: reactor.stop())

            reactor.run(0)

        except Exception as e:
            return

    p = Process(target=process, args=(target, callback))
    p.start()
    print(p.join())
    print('DONE')
