#!/usr/bin/env python3

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings  # to run multiple spiders at the same time
import csv
import os
import logging

settings = get_project_settings()  # permet d'enregistrer le résultat des scrapings sur un seul fichier
process = CrawlerProcess(settings)

# pour formater le fichier des urls à scrapper on se sert du module 'csv'
with open('all_urls.csv', newline='') as f:
    reader = csv.reader(f)
    data = list(reader)

# on va créer des listes d'urls pour chaque site scrappé:
listAZ = []
listjdf = []
list750g = []
listmarmiton = []

for i in range(len(data)):
    for url in data:
        try:
            if 'cuisineaz' in url[i]:
                listAZ.append(url[i])
        except IndexError:
            continue
        try:
            if 'journaldesfemmes' in url[i]:
                listjdf.append(url[i])
        except IndexError:
            continue
        try:
            if '750g' in url[i]:
                list750g.append(url[i])
        except IndexError:
            continue
        try:
            if 'marmiton' in url[i]:
                listmarmiton.append(url[i])
        except IndexError:
            continue


class CuisineAZ(scrapy.Spider):
    name = "after_search"

    def start_requests(self):
        for url in listAZ:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        yield {'titre': response.css('h1.recipe-title ::text').get(),
               'url': response.xpath("//meta[@property='og:url']/@content").get(),
               'note': 0.5 * (
                   response.css('div.rating-foreground.cazStars span.hidden-link span.icon-half-star').getall().count(
                       '<span class="icon-half-star"></span>')) + (
                           response.css('div.rating-foreground.cazStars div.icon-star').getall().count(
                               '<div class="icon-star"></div>')),
               'Nbre vote, avis ou commentaires': response.css('span.smoothScroll.pointer b::text').get(),
               'niveau de difficulté': response.css('div.icon-toque::text').get(),
               'temps de préparation (en min)': response.css('#ContentPlaceHolder_LblRecetteTempsPrepa::text').get(),
               'temps de cuisson (en min)': response.css('#ContentPlaceHolder_LblRecetteTempsCuisson::text').get(),
               'ingrédients': ' '.join(response.css('span.ingredient_label::text').getall()),
               }


class Jdfscrape(scrapy.Spider):
    name = 'jdf_global'

    def start_requests(self):
        for url in listjdf:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        yield {'titre': response.css('h1.app_recipe_title_page::text').get(),
               'url': response.xpath("//meta[@name='og:url']/@content").get(),
               'note': response.css('span.jAverage ::text').get(),
               'Nbre vote, avis ou commentaires': response.css('span.jNbNote ::text').get(),
               'niveau de difficulté': response.css('div.grid_last ul.bu_cuisine_carnet_2 li::text').get(),
               'temps de préparation (en min)': response.css('span.duration::text').get(),
               'temps de cuisson (en min)':
                   response.css('div.grid_last ul.bu_cuisine_carnet_2 li span::text').getall()[1],
               'ingrédients': ' '.join(response.css('div.grid_left ul.bu_cuisine_ingredients li a::text').getall()),
               }


class g750scrape(scrapy.Spider):
    name = '750_global'

    def start_requests(self):
        for url in list750g:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        yield {'titre': response.css('span.u-title-page.u-align-center::text').get(),
               'url': response.xpath("//meta[@property='og:url']/@content").get(),
               'note': response.css('span.u-bold ::text').get(),
               'Nbre vote, avis ou commentaires': response.css('span.rating-votes ::text').get(),
               'niveau de difficulté': response.css('div.recipe-info ::text').getall()[4],
               'temps de préparation (en min)':
                   response.css('div.grid.recipe-steps-info.u-margin-bottom.u-align-center ::text').getall()[3],
               'temps de cuisson (en min)':
                   response.css('div.grid.recipe-steps-info.u-margin-bottom.u-align-center ::text').getall()[7],
               'ingrédients': ' '.join(response.css('section.recipe-section.recipe-ingredients span::text').getall()),
               }


class Marmitonscrape(scrapy.Spider):
    name = 'marmiton_global'

    def start_requests(self):
        for url in listmarmiton:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        yield {'titre': response.css('h1.SHRD__sc-10plygc-0.itJBWW::text').get(),
               'url': response.xpath("//meta[@property='og:url']/@content").get(),
               'note': response.css('span.SHRD__sc-10plygc-0.jHwZwD::text').get(),
               'Nbre vote, avis ou commentaires': response.css('span.SHRD__sc-10plygc-0.cAYPwA::text').get(),
               'niveau de difficulté': response.css('p.RCP__sc-1qnswg8-1.iDYkZP::text').getall()[1],
               'temps de préparation (en min)': response.css('span.SHRD__sc-10plygc-0.bzAHrL::text').getall()[1],
               'temps de cuisson (en min)': response.css('span.SHRD__sc-10plygc-0.bzAHrL::text').getall()[3],
               'ingrédients': ' '.join(response.css('div.RCP__sc-vgpd2s-1.fLWRho span::text').getall()),
               }


filename = "final_scraping.csv"
if filename in os.listdir():
    os.remove(filename)

process = CrawlerProcess(settings={
    **settings,
    'USER_AGENT': 'Chrome/84.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'LOG_LEVEL': logging.INFO,
    'AUTOTHROTTLE_ENABLED': True,  # to help avoid being banned
    "FEEDS": {
        filename: {"format": "csv"},
    }
})

process.crawl(CuisineAZ)
process.crawl(Jdfscrape)
process.crawl(g750scrape)
process.crawl(Marmitonscrape)
process.start()  # the script will block here until all crawling jobs are finished

#os.system('python3 test_cleaning.py')