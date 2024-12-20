# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from collections import OrderedDict


class ImdbscraperItem(scrapy.Item):
    fields = OrderedDict([
        ('movie_id', scrapy.Field()),
        ('title', scrapy.Field()),
        ('ranking', scrapy.Field()),
        ('release_year', scrapy.Field()),
        ('runtime', scrapy.Field()),
        ('rating', scrapy.Field()),
        ('vote_count', scrapy.Field()),
        ('certificate', scrapy.Field()),
        ('description', scrapy.Field()),
    ])

class BoxofficeFinancialsItem(scrapy.Item):
    fields = OrderedDict([
        ('movie_id', scrapy.Field()),
        ('domestic_opening', scrapy.Field()),
        ('domestic_revenue', scrapy.Field()),
        ('international_revenue', scrapy.Field()),
        ('budget', scrapy.Field()),
    ])

class BoxofficeProductionItem(scrapy.Item):
    fields = OrderedDict([
        ('movie_id', scrapy.Field()),
        ('domestic_distributor', scrapy.Field()),
        ('genres', scrapy.Field()),
        ('director', scrapy.Field()),
        ('movie_casts', scrapy.Field()),
    ])

class BoxofficeArticleItem(scrapy.Item):
    fields = OrderedDict([
        ('movie_id', scrapy.Field()),
        ('article_title', scrapy.Field()),
        ('article_id', scrapy.Field()),
        ('article_link', scrapy.Field()),
        ('publication_date', scrapy.Field()),
    ])