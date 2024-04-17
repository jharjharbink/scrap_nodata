# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Item, Field


class ReleaseItem(Item):
    artist_name = Field()
    release_name = Field()
    released_year = Field()
    published_date = Field()
    tag_list = Field()
    format = Field()
    comment_number = Field()
    image_urls = Field()
    all_songs_and_length = Field()
    label_name = Field()
    release_url = Field()
    images = Field()


class ScrapingItem(Item):
    artist_name_release_name_released_year = Field()
    published_date = Field()
    tag_list = Field()
    comment_number = Field()
    image_urls = Field()
    all_songs = Field()
    label_name = Field()
    release_url = Field()

