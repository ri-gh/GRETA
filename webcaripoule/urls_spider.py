#!/usr/bin/env python3
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings  # to run multiple spiders at the same time
import os
import logging

settings = get_project_settings()  # permet d'enregistrer le résultat des scrapings sur un seul fichier
process = CrawlerProcess(settings)

# variable qui devra être renseignée par le user sur le site django
# recette = input('Quelle recette cherchez vous ? ')
def run(recette):
    """
    Scrappe les urls de chaque recette sur chacun des sites et enregistre un fichier
    de résultats sur le répertoire local
    Lance le programme de scrapping des détails des recettes sur chaque URL
    collecté
    """
    recette_clean = recette.replace('+', ' ')
    recette_clean = recette_clean.split()[0]  # on va filtrer les urls par ceux qui contiennent un mot clé

    class CuisineAZ(scrapy.Spider):
        name = "after_search"
        start_urls = [f'https://www.cuisineaz.com/recettes/recherche_terme.aspx?recherche={recette}']

        def parse(self, response):
            result = response.css('#result.tile.searchResult')
            for r in result:
                if recette_clean in f"https://www.cuisineaz.com/{r.css('h2.tile_title a.txtgrey::attr(href)').get()}":
                    yield {'url': f"https://www.cuisineaz.com/{r.css('h2.tile_title a.txtgrey::attr(href)').get()}"}

                    next_page = response.css(
                        'li.pagination-next span a::attr(href)').get()  # on récupère l'url pour aller à la page suivante
                    if next_page is not None:
                        next_page = response.urljoin(
                            next_page)  # urljoin permet de créer un lien avec url de base + next page
                        yield scrapy.Request(next_page, callback=self.parse)

    class JdfUrl(scrapy.Spider):
        name = "jdf_scrap"
        start_urls = [f'https://cuisine.journaldesfemmes.fr/s/?f_libelle={recette}']

        def parse(self, response):
            result = response.css('section.grid_line.gutter.grid--norwd.bu_cuisine_mod_search div.grid_left.w70 ')
            for r in result:
                if recette_clean in r.css('p.bu_cuisine_recette_title a::attr(href)').get():
                    yield {
                        'url': r.css('p.bu_cuisine_recette_title a::attr(href)').get(),
                    }

                next_page = response.css(
                    'div.ccmcss_paginator_next a::attr(href)').get()  # on récupère l'url pour aller à la page suivante
                if next_page is not None:
                    next_page = response.urljoin(
                        next_page)  # urljoin permet de créer un lien avec url de base + next page
                    yield scrapy.Request(next_page, callback=self.parse)

    class W750g(scrapy.Spider):
        name = "750g"
        start_urls = ['https://www.750g.com/recherche/?q=' + recette]

        def parse(self, response):
            # on obtient une page de résultat mais on veut récupérer les urls pour toutes les recettes
            # ici sur la première page
            results = response.css('div.is-12 div.card-content')
            for r in results:
                if recette_clean in r.css('a.card-link::attr(href)').get():
                    yield {'url': r.css('a.card-link::attr(href)').get()}

                # pour scraper les pages suivantes , on prend le parti de dire qu'il n'y aura pas plus de 18 pages de résultat
                for i in range(2, 19):
                    next_page = "https://www.750g.com/recherche/?q=" + recette + f"&page={i}"
                    yield response.follow(next_page, callback=self.parse)

    class Marmiton(scrapy.Spider):
        name = "marmiton"
        start_urls = ['https://www.marmiton.org/recettes/recherche.aspx?aqt=' + recette]

        def parse(self, response):
            result = response.css('a.MRTN__sc-1gofnyi-2.gACiYG')
            for r in result:
                if recette_clean in f"https://www.marmiton.org{r.css('::attr(href)').get()}":
                    yield {'url': f"https://www.marmiton.org{r.css('::attr(href)').get()}", }

                for i in range(2, 11):
                    next_page = 'https://www.marmiton.org/recettes/recherche.aspx?aqt=' + recette + f'&page={i}'
                    yield scrapy.Request(next_page, callback=self.parse)

    # on définit une fonction qui va lancer le scraping et la création des fichiers de données

    filename = "all_urls.csv"
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
    process.crawl(JdfUrl)
    process.crawl(W750g)
    process.crawl(Marmiton)
    process.start(stop_after_crawl=True,
                  install_signal_handlers=False)  # the script will block here until all crawling jobs are finished

    # pour démarrer le second script qui va scrapper les détails des recettes sur les urls récupérées ici
    os.system('python3 webcaripoule/global_spider.py')


def main():  # on définit une fonction 'main' pour tester la classe dans ce fichier uniquement
    run()


if __name__ == '__main__':
    main()

