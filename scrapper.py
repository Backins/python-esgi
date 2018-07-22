# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request, HtmlResponse
from urllib.parse import urlparse

class ScrapResultItem(scrapy.Item):
    url = scrapy.Field()


class WebSpider(scrapy.Spider):
    name = 'webcrawler'


    def __init__(self, **kw):
        super(WebSpider, self).__init__(**kw)

        #  On stocke dans la variable url le site à crawler.
        url = kw.get('target')

        #  On s'assure que le lien à crawler contient bien http:// ou https://
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'http://%s/' % url

        self.url = url

        #  On evite de taper sur les autres sites que celui indiqué par le crawler.
        self.allowed_domains = [urlparse(url).hostname]

        #  On declare notre fonction chargée de l'extraction des liens.
        self.link_extractor = LinkExtractor()

        #  On initialise le stockage.
        self.storage[self.url] = []


    def start_requests(self):
        #  On envoie les requêtes!
        return [Request(self.url, callback=self.parse, dont_filter=True)]


    def parse(self, response):
        #  On stocke un objet qui pointe vers l'URL que l'on vient de crawler (afin deviter les duplicats)
        page = ScrapResultItem(url=response.url)

        #  On ajoute dans le storage, toutes les informations que l'on veut retourner a l'utilisateur.
        self.storage[self.url].append({'url': response.url, 'len': len(response.body), 'status': response.status})

        r = [page]

        #  On extrait les differents liens de la page que l'on traite par la suite.
        r.extend(self._extract_requests(response))
        return r


    def _extract_requests(self, response):
        r = []
        if isinstance(response, HtmlResponse):
            #  On parse les differents liens...
            links = self.link_extractor.extract_links(response)
            r.extend(Request(x.url, callback=self.parse) for x in links)
        return r
