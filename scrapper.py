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

        # FR - HELP On stocke dans la variable url le site à crawler.
        # EN - HELP Stock in the :param url, the website to crawl
        url = kw.get('target')

        # FR - HELP On s'assure que le lien à crawler contient bien http:// ou https://
        # EN - HELP Verify the url website, we need http:// or https://
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'http://%s/' % url

        self.url = url

        # FR - HELP On evite de taper sur les autres sites que celui indiqué par le crawler.
        # EN - HELP It's use to not targeted the other website
        self.allowed_domains = [urlparse(url).hostname]

        # FR - HELP On declare notre fonction chargée de l'extraction des liens.
        # EN - HELP We declare our function where we extract the url
        self.link_extractor = LinkExtractor()

        # FR - HELP On initialise le stockage.
        # EN - HELP Initialize storage
        self.storage[self.url] = []

    def start_requests(self):
        # FR - HELP On envoie les requêtes!
        # EN - HELP We send the request
        return [Request(self.url, callback=self.parse, dont_filter=True)]

    def parse(self, response):
        # FR - HELP On stocke un objet qui pointe vers l'URL que l'on vient de crawler (afin deviter les duplicats)
        # EN - HELP Storage object which target the URL when we crawl
        page = ScrapResultItem(url=response.url)

        # FR - HELP On ajoute dans le storage, toutes les informations que l'on veut retourner a l'utilisateur.
        # EN - HELP We add in the storage, all data that we need to return at the user
        self.storage[self.url].append({'url': response.url, 'len': len(response.body), 'status': response.status})

        r = [page]

        # FR - HELP On extrait les differents liens de la page que l'on traite par la suite.
        # EN - HELP We extract the different link of the page
        r.extend(self._extract_requests(response))
        return r

    def _extract_requests(self, response):
        r = []
        if isinstance(response, HtmlResponse):
            # FR - HELP On parse les differents liens...
            # EN - HELP We parsed the different link
            links = self.link_extractor.extract_links(response)
            r.extend(Request(x.url, callback=self.parse) for x in links)
        return r
