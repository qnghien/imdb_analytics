import scrapy
import csv
import os
from urllib.parse import urljoin
from imdbscraper.items import BoxofficeFinancialsItem, BoxofficeProductionItem, BoxofficeArticleItem
from imdbscraper.utils.url_generator import generate_financials_url, generate_production_url, generate_articles_url
from imdbscraper.utils.db_utils import fetch_top_250_movie_ids

class BoxOfficeSpider(scrapy.Spider):
    name = "box_office"
    allowed_domains = ["www.boxofficemojo.com"]
    start_urls = ["https://www.boxofficemojo.com/title/"]

    def start_requests(self):
        # Code for taking movie_id from imtermmediate csv file
        # csv_file = os.path.join(os.path.dirname(__file__), "../output/movie_info.csv")

        # if not os.path.exists(csv_file):
        #     self.logger.error(f"File not found in this directory: {csv_file}")
        #     return
        
        # with open(csv_file, mode = 'r', encoding = 'utf-8') as imdbfile:
        #     reader = csv.DictReader(imdbfile)
        #     for row in reader:
        #         if 'movie_id' in row:
        #             movie_id = row['movie_id']
        #             financials_url = generate_financials_url(movie_id) # do this later
        #             # print(financials_url)
        #             yield scrapy.Request(financials_url, meta={"movie_id": movie_id, "stage": "financial"})

        # fetch movie_id from database for crawling
        movie_ids = fetch_top_250_movie_ids()

        if not movie_ids:
            self.logger.error("No movie IDs found in the database")
            return
        
        for movie_id in movie_ids:
            financials_url = generate_financials_url(movie_id)
            yield scrapy.Request(financials_url, meta = {"movie_id": movie_id, "stage": "financial"})
        

    def parse(self, response):
        movie_id = response.meta["movie_id"]
        stage = response.meta["stage"]
        # Financials data
        if stage == "financial": 
            finance_item = BoxofficeFinancialsItem()
            
            finance_item['movie_id'] = movie_id
            finance_item['domestic_opening'] = response.css("div.mojo-hidden-from-mobile span.money::text").getall()[0] # change all rev to standard format
            finance_item['domestic_revenue'] = response.css("div.mojo-performance-summary span.money::text").getall()[0] # change all rev to standard format
            finance_item['international_revenue'] = response.css("div.mojo-performance-summary span.money::text").getall()[1] # change all rev to standard format
            finance_item['budget'] = response.css("div.mojo-hidden-from-mobile span.money::text").getall()[1] # change all rev to standard format

            yield finance_item

            # Follow the next link to scrap production data
            production_url = generate_production_url(movie_id)
            yield scrapy.Request(production_url, meta = {"movie_id" : movie_id, "stage": "production"})
        
        elif stage == "production":
            production_item = BoxofficeProductionItem()

            production_item['movie_id'] = movie_id
            production_item['domestic_distributor'] = response.css(".a-section.mojo-summary-values.mojo-hidden-from-mobile .a-spacing-none span::text").getall()[1]
            production_item['genres'] = response.css(".a-section.mojo-summary-values.mojo-hidden-from-mobile .a-spacing-none span::text").getall()[-2]
            production_item['director'] = response.css('#principalCrew a[href*="/name/"]::text').get() # will need text-preprocess
            production_item['movie_casts'] = response.css('#principalCast a[href*="/name/"]::text').getall()

            yield production_item

            # Follow the next link to scrap related articles data
            article_url = generate_articles_url(movie_id)
            yield scrapy.Request(article_url, meta = {"movie_id" : movie_id, "stage": "article"})
        
        elif stage == "article":
            try:
                rows = response.css('div.a-section.mojo-gutter table tr')[1:]
                for article in rows:
                    if not article.css('td a.a-link-normal::text'):
                        continue
                    article_item = BoxofficeArticleItem()

                    article_item['movie_id'] = movie_id
                    article_item['article_title'] = article.css('td a.a-link-normal::text').get() 
                    article_item['article_id'] = article.css('td a.a-link-normal::attr(href)').get().split('/')[2]
                    article_item['article_link'] = urljoin("https://www.boxofficemojo.com/article/", article.css('td a.a-link-normal::attr(href)').get()) # will need to urljoin with root link
                    article_item['publication_date'] = article.css('td span.a-color-secondary::text').get() # will need to change to standard format


                    yield article_item

            except Exception as e:
                self.logger.warning(f"No articles found for movie_id {movie_id}: {e}")