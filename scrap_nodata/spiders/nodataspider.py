import scrapy
from scrapy.loader import ItemLoader
from scrap_nodata.items import ReleaseItem, ScrapingItem

from scrapy import Selector


class NodataspiderSpider(scrapy.Spider):
    name = "nodataspider"
    allowed_domains = ["nodata.tv"]
    start_urls = ["https://nodata.tv/blog/page/1"]

    def parse(self, response):

        # get all releases page's url on main page
        release_items = response.css('a.title::attr(href)').extract()

        for release_item in release_items:

            # for each release page, go to it and call the parse_release_page() method to scrap the data
            yield response.follow(release_item, callback=self.parse_release_page)

        # Once we scraped all the album on page, we move to next main page
        next_page_url = response.css('li.last a::attr(href)').get()

        if next_page_url is not None:
            yield response.follow(next_page_url, callback=self.parse)

    @staticmethod
    def parse_release_page(response):

        artist_name_release_name_released_year = response.css('div.page-heading h4::text').get()

        published_date = response.css('ul.meta li:nth-child(2)::text').get()

        tag_list = response.css('ul.meta a[rel="category tag"]::text').extract()

        comment_number = response.css('ul.meta li:last-child a::text').get()

        release_image_url = response.css('img::attr(src)').get()

        try:
            all_songs = response.css('ol li::text').extract()
        except:
            all_songs = None  # won't be set if no songs available

        try:
            label_name = response.xpath('//span[@class="aligncenter"]/following::text()').get()
        except:
            label_name = None  # won't be set if no songs available

        yield ScrapingItem(
            artist_name_release_name_released_year=artist_name_release_name_released_year,
            published_date=published_date,
            tag_list=tag_list,
            comment_number=comment_number,
            release_image_url=release_image_url,
            all_songs=all_songs,
            label_name=label_name,
            album_url=response.request.url
        )

# class NodataspiderSpider(scrapy.Spider):
#     name = "nodataspider"
#     allowed_domains = ["nodata.tv"]
#     start_urls = ["https://nodata.tv/blog/page/1"]
#
#     def parse(self, response):
#
#         release_items = response.css('.project-box')
#
#         for counter, release_item in enumerate(release_items):
#
#             if counter > 0:
#                 break
#
#             # Extract ['tag1', 'tag2', ..., 'artist_name / release_name [released_year]', 'comment_number']
#             all_text_elements = release_item.css('.project-box div.object').xpath('.//text()').extract()
#             all_text_elements_cleaned = filter_comma_linefeed_and_tabulations(all_text_elements, ", \n\t")
#
#             # Extract artist_name and release_name from all_text_elements_cleaned[-3]
#             artist_release = all_text_elements_cleaned[-3].split(' [')[0]  # Exclure les données entre crochets
#             separator = ' / ' if ' / ' in artist_release else ' - '
#             artist_name, release_name = artist_release.split(separator)
#
#             #  Extract tags from all_text_elements_cleaned
#             tags = all_text_elements_cleaned[:-3]
#
#             # Set release_type to None to preprocess it in pipelines. release_type value will be one of the tags
#             # Album is the value by default
#             # loader.add_value('release_type', "Album")
#
#             # Extract released_year from all_text_elements_cleaned
#             if all_text_elements_cleaned[-3][-7:-5] == ' [' and all_text_elements_cleaned[-3][-1] == ']':
#                 released_year = all_text_elements_cleaned[-3][-6:]
#             else:
#                 released_year = None
#
#             # Extract comment_number from all_text_elements_cleaned
#             comment_number = all_text_elements_cleaned[-1]
#
#             # Extract release's page url
#             release_url = release_item.css('.project-box a.title::attr(href)').get()
#
#             # extract image url
#             release_image_url = release_item.css('.project-box img::attr(src)').get()
#
#             loader = ItemLoader(
#                 artist_name=artist_name,
#                 release_name=release_name,
#                 tags=tags,
#                 released_year=released_year,
#                 comment_number=comment_number,
#                 release_url=release_url,
#                 release_image_url=release_image_url
#             )
#
#             # Follow the release page and pass album_data via meta
#             yield response.follow(release_url, self.parse_release, meta={'loader': loader})
#
#         next_page_url = response.css('li.last a::attr(href)').get()
#
#         # if next_page_url is not None:
#         #     yield response.follow(next_page_url, callback=self.parse)
#
#     def parse_release(self, response):
#
#         loader = response.meta['loader']
#
#         # extract the music_list
#         all_songs = response.css('ol li::text').extract()
#
#         # Add the remaining data to the loader
#         loader.add_value('all_songs', filter_comma_linefeed_and_tabulations(all_songs))
#         loader.add_value('label_name', response.xpath('//span[@class="aligncenter"]/following::text()').get().strip())
#         loader.add_value('published_date', response.css('ul.meta li::text').extract()[1])
#
#         yield loader.load_item()


#  scrapy shell
#  fetch('https://nodata.tv/blog')
#  album_items = response.css('.project-box')
#  album_page_href = album_items.css('.project-box a.title::attr(href)').get()
#  fetch(album_page_href)
