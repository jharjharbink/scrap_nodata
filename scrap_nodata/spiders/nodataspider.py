import scrapy
from scrap_nodata.items import ScrapingItem


from scrap_nodata.logger import logger

from time import sleep


class NodataspiderSpider(scrapy.Spider):
    name = "nodataspider"
    allowed_domains = ["nodata.tv"]
    start_urls = ["https://nodata.tv/blog/page/1"]

    def parse(self, response):

        logger.info(f"current main page: {response.request.url}")

        # get all releases page's url on main page
        try:
            release_items = response.css('a.title::attr(href)').extract()
        except Exception as ex:
            logger.error(f"{ex}\nunable to catch releases urls. Current page: {response.request.url}")
            release_items = list()

        for release_item in release_items:

            # for each release page, go to it and call the parse_release_page() method to scrap the data
            try:
                logger.info(f"reaching release page: {release_item}")
                yield response.follow(release_item, callback=self.parse_release_page)
            except Exception as ex:
                logger.error(ex)
                logger.error(f"unable to go to release url: {release_item}")

        # Once we scraped all the album on page, we move to next main page
        try:
            next_page_url = response.css('li.last a::attr(href)').get()
            if next_page_url is not None:
                yield response.follow(next_page_url, callback=self.parse)
        except Exception as ex:
            logger.error(f"{ex}\nunable to reach next page. Next page: {next_page_url}")


    @staticmethod
    def parse_release_page(response):
        logger.info(f"next page reached: {response.request.url}")

        sleep(1)

        try:
            artist_name_release_name_released_year = response.css('div.page-heading h4::text').get()
            published_date = response.css('ul.meta li:nth-child(2)::text').get()
            tag_list = response.css('ul.meta a[rel="category tag"]::text').extract()
            comment_number = response.css('ul.meta li:last-child a::text').get()
            release_image_url = [response.css('img::attr(src)').get()]  # putting in a list for it to be proccessed by scrapy media pipeline
            all_songs = response.css('ol li::text').extract()
            label_name = response.xpath('//span[@class="aligncenter"]/following::text()').get()

            logger.info(f"data collected:\n- artist_name_release_name_released_year: "
                        f"{artist_name_release_name_released_year}\n- published_date: {published_date}\n - tag_list: \n"
                        f"{tag_list}\n - comment_number: {comment_number}\n- release_image_url: {release_image_url}\n- "
                        f"all_songs: {all_songs}\n- label_name: {label_name}")

        except Exception as ex:
            logger.warning(f"{ex}\nunable to get data for page: {response.request.url}")

            artist_name_release_name_released_year = None
            published_date = None
            tag_list = None
            comment_number = None
            release_image_url = None
            all_songs = None
            label_name = None

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


class DebugNodataspiderSpider(scrapy.Spider):
    name = "debug_nodataspider"
    allowed_domains = ["nodata.tv"]
    start_urls = ["https://nodata.tv/192271"]

    def parse(self, response):


        try:
            artist_name_release_name_released_year = response.css('div.page-heading h4::text').get()
            published_date = response.css('ul.meta li:nth-child(2)::text').get()
            tag_list = response.css('ul.meta a[rel="category tag"]::text').extract()
            comment_number = response.css('ul.meta li:last-child a::text').get()
            release_image_url = [response.css('img::attr(src)').get()]  # putting in a list for it to be proccessed by scrapy media pipeline
            all_songs = response.css('ol li::text').extract()
            label_name = response.xpath('//span[@class="aligncenter"]/following::text()').get()

            logger.info(f"data collected:\n- artist_name_release_name_released_year: "
                        f"{artist_name_release_name_released_year}\n- published_date: {published_date}\n - tag_list: \n"
                        f"{tag_list}\n - comment_number: {comment_number}\n- release_image_url: {release_image_url}\n- "
                        f"all_songs: {all_songs}\n- label_name: {label_name}")

        except Exception as ex:
            logger.warning(f"{ex}\nunable to get data for page: {response.request.url}")

            artist_name_release_name_released_year = None
            published_date = None
            tag_list = None
            comment_number = None
            release_image_url = None
            all_songs = None
            label_name = None

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