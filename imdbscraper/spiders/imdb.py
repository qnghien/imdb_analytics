import scrapy
import json
from imdbscraper.items import ImdbscraperItem

class ImdbSpider(scrapy.Spider):
    name = "imdb"
    allowed_domains = ["imdb.com"]
    start_urls = ["https://www.imdb.com/chart/top/"]

    def parse(self, response):
        
        page_script = response.css("script[id='__NEXT_DATA__']::text").get()
        json_script = json.loads(page_script)
        json_data = json_script['props']['pageProps']['pageData']['chartTitles']['edges']

        movie = ImdbscraperItem()
        for item in json_data:

            movie['movie_id'] = item['node']['id']
            movie['title'] = item['node']['titleText']['text']
            movie['ranking'] = item['currentRank']
            movie['release_year'] = item['node']['releaseYear']['year']
            movie['runtime'] = item['node']['runtime']['seconds']
            movie['rating'] = item['node']['ratingsSummary']['aggregateRating']
            movie['vote_count'] = item['node']['ratingsSummary']['voteCount']
            movie['certificate'] = item['node']['certificate']
            movie['description'] = item['node']['plot']['plotText']['plainText']

            yield movie
        

