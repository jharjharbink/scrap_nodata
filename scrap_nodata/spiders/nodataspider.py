import requests
import scrapy
from scrapy.loader import ItemLoader
from scrap_nodata.items import ReleaseItem, ScrapingItem

from scrapy import Selector

from scrap_nodata.logger import logger

from time import sleep


class NodataspiderSpider(scrapy.Spider):
    name = "nodataspider"
    allowed_domains = ["nodata.tv"]
    start_urls = ["https://nodata.tv/blog/page/1"]

    def parse(self, response):

        # get all releases page's url on main page
        try:
            release_items = response.css('a.title::attr(href)').extract()
        except Exception as ex:
            logger.error(ex)
            logger.error(f"unable to catch releases urls. Current page: {response.request.url}")

        for release_item in release_items:

            # for each release page, go to it and call the parse_release_page() method to scrap the data
            try:
                yield response.follow(release_item, callback=self.parse_release_page)
            except Exception as ex:
                logger.error(ex)
                logger.error(f"unable to go to release url: {release_item}")

        # Once we scraped all the album on page, we move to next main page
        try:
            next_page_url = response.css('li.last a::attr(href)').get()
        except Exception as ex:
            logger.error(ex)
            logger.error(f"unable to catch next page. Current page: {response.request.url}")

        # try:
        #     if next_page_url is not None:
        #         yield response.follow(next_page_url, callback=self.parse)
        # except Exception as ex:
        #     logger.error(ex)
        #     logger.error(f"unable to reach next page. Next page: {next_page_url}")


    @staticmethod
    def parse_release_page(response):

        sleep(1)

        try:
            artist_name_release_name_released_year = response.css('div.page-heading h4::text').get()
        except Exception as ex:
            logger.warning(ex)
            logger.warning(f"unable to get artist_name_release_name_released_year for page : {response.request.url}")

        try:
            published_date = response.css('ul.meta li:nth-child(2)::text').get()
        except Exception as ex:
            logger.warning(ex)
            logger.warning(f"unable to get published_date for page : {response.request.url}")

        try:
            tag_list = response.css('ul.meta a[rel="category tag"]::text').extract()
        except Exception as ex:
            logger.warning(ex)
            logger.warning(f"unable to get tag_list for page : {response.request.url}")

        try:
            comment_number = response.css('ul.meta li:last-child a::text').get()
        except Exception as ex:
            logger.warning(ex)
            logger.warning(f"unable to get comment_number for page : {response.request.url}")

        try:
            release_image_url = [response.css('img::attr(src)').get()]  # putting in a list for it to be proccessed by scrapy media pipeline
        except Exception as ex:
            logger.warning(ex)
            logger.warning(f"unable to get release_image_url for page : {response.request.url}")

        try:
            all_songs = response.css('ol li::text').extract()
        except Exception as ex:
            logger.info(ex)
            all_songs = None  # won't be set if no songs available
            logger.info(f"unable to get songs for page : {response.request.url}")

        try:
            label_name = response.xpath('//span[@class="aligncenter"]/following::text()').get()
        except Exception as ex:
            logger.warning(ex)
            label_name = None  # won't be set if label not available
            logger.info(f"unable to get label_name for page : {response.request.url}")

        try:
            yield ScrapingItem(
                artist_name_release_name_released_year=artist_name_release_name_released_year,
                published_date=published_date,
                tag_list=tag_list,
                comment_number=comment_number,
                image_urls=release_image_url,
                all_songs=all_songs,
                label_name=label_name,
                release_url=response.request.url
            )
        except Exception as ex:
            logger.warning(ex)
            logger.warning(f"unable to yield ScrapingItem for release at page: {response.request.url}")


