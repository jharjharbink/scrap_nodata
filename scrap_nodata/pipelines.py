# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from datetime import datetime
from contextlib import contextmanager

from sqlalchemy.orm import Session

from scrap_nodata.db.tables import Tag, Release, Song
from scrap_nodata.db.scripts.usefull_functions import get_engine
from scrap_nodata.items import ReleaseItem
from scrap_nodata.logger import logger


RELEASE_FORMATS = (
    "remixes",
    "single",
    "ep",
    "album",
    "compilation",
    "Documentary",
    "demo",
    "dvd",
    "mixtape",
    "unknown",
    "dj mix"
)


class PostProcessingPipeline:
    def process_item(self, item, spider):

        try:
            if 'artist_name_release_name_released_year' in item:
                artist_name, release_name, released_year = self.extract_artist_release_and_year(
                    item['artist_name_release_name_released_year'])
            else:
                artist_name = ""
                release_name = ""
                released_year = 1000

        except Exception as exc:
            logger.warning(f"{exc}\nUnable to extract artist_name, release_name and released_year for item: {item.items()}")
            artist_name = ""
            release_name = ""
            released_year = 1000

        # Format published_date from 'Sep 08, 2023 ·' to Date(08/09/2023)
        try:
            if 'published_date' in item:
                published_date = self.extract_published_year(item["published_date"])
            else:
                published_date = None  # remplacer par Date(00/00/1000)

        except Exception as exc:
            logger.warning(f"{exc}\nUnable to parse published_date for item: {item.items()}")
            published_date = None  # remplacer par Date(00/00/1000)

        try:
            if 'tag_list' in item:
                tag_list, release_type = self.remove_format_from_tags(item['tag_list'])
            else:
                tag_list = []
                release_type = "unknown"
        except Exception as exc:
            logger.warning(f"{exc}\nUnable to parse tag_list for item: {item.items()}")
            tag_list = []
            release_type = "unknown"

        # Format comment_number from 'No comments' to 0
        try:
            if 'comment_number' in item:
                comment_number = self.extract_comment_number(item['comment_number'][0])
            else:
                comment_number = -1

        except Exception as exc:
            logger.warning(f"{exc}\nUnable to parse comment_number for item: {item.items()}")
            comment_number = -1

        try:
            if 'all_songs' in item:
                all_songs_and_length = self.extract_songs_and_length(item['all_songs'], comment_number)
            else:
                all_songs_and_length = []

        except (KeyError, ValueError) as exc:
            logger.info(f"{exc}\nall_songs unavailable for this item: {item.items()}")
            all_songs_and_length = []

        try:
            if 'label_name' in item:
                label_name = self.filter_label(item['label_name'])
            else:
                label_name = ""

        except KeyError as exc:
            logger.info(f"{exc}\nlabel_name unavailable for this item: {item.items()}")
            label_name = ""

        return ReleaseItem(
            artist_name=artist_name,
            release_name=release_name,
            released_year=released_year,
            published_date=published_date,
            tag_list=tag_list,
            format=release_type,
            comment_number=comment_number,
            image_urls=item['image_urls'],
            all_songs_and_length=all_songs_and_length,
            label_name=label_name,
            release_url=item['release_url'])

    def remove_format_from_tags(self, tags):

        lower_cased_values = [item.lower() for item in tags]

        release_type_tags = [item for item in lower_cased_values if item in RELEASE_FORMATS]

        release_type = self.map_release_format(release_type_tags)

        tags = [item for item in lower_cased_values if item not in release_type]

        return tags, release_type

    @staticmethod
    def extract_artist_release_and_year(all_text_elements):
        """
        all_text_elements can be like :
        s1 = "Daniel Avery – Wonderland / Running [2024]"
        s2 = "Daniel Avery – Wonderland / Running"
        s3 = "Daniel Avery / Wonderland - Running [2024]"
        s4 = "Daniel Avery / Wonderland - Running"

        the idea is to parse all of those string types to: "Daniel Avery", "Wonderland - Running", "2024"/None
        """

        all_text_elements_cleaned = all_text_elements.strip().replace('\xa0', ' ').replace('\u200e', ' ')

        # Extract artist_name and release_name from all_text_elements
        artist_release = all_text_elements_cleaned.rsplit(' [', 1)[0]

        if ' / ' in artist_release and ' – ' in artist_release:
            if artist_release.count(' / ') > 1 and artist_release.count(' – ') == 1:
                separator = ' – '

            elif artist_release.count(' – ') > 1 and artist_release.count(' / ') == 1:
                separator = ' / '

            else:
                if artist_release.find(' / ') < artist_release.find(' – '):
                    separator = ' / '
                else:
                    separator = ' – '
        else:
            if ' / ' in artist_release:
                separator = ' / '
            else:
                separator = ' – '

        artist_name, release_name = artist_release.rsplit(separator, 1)

        # Extract released_year from all_text_elements_cleaned
        if all_text_elements_cleaned[-7:-5] == ' [' and all_text_elements_cleaned[-1] == ']':
            released_year = int(all_text_elements_cleaned[-5:-1])
        else:
            released_year = None

        return artist_name, release_name, released_year

    @staticmethod
    def extract_published_year(published_year_raw):
        date_object_cleaned = published_year_raw.strip().replace('\xa0', ' ').replace('\u200e', ' ')

        date_object_cleaned = datetime.strptime(date_object_cleaned, '%b %d, %Y')
        date_object = date_object_cleaned.strftime('%d/%m/%Y')
        return date_object

    @staticmethod
    def extract_comment_number(comment_number_raw):
        if comment_number_raw.isdigit():
            comment_number = int(comment_number_raw.split(' ')[0])  # Extraire le nombre de commentaires
        else:
            comment_number = 0  # S'il n'y a pas de commentaires, mettre 0
        return comment_number

    @staticmethod
    def map_release_format(format_list):
        """
        Sometimes, albums contains multiple tags to describe their type of record (format), which are in conflict. this are
        all the combinations that I found and the priority associated
        """

        if len(format_list) == 0:  # if there is no format, there is no conflict.
            return "unknown"
        elif len(format_list) == 1:
            return format_list[0]  # if there is 1 format, there is no conflict.
        elif set(format_list) == {"album", "remixes"}:
            return "remixes"
        elif set(format_list) == {"ep", "remixes"}:
            return "remixes"
        elif set(format_list) == {"remixes", "single"}:
            return "remixes"
        elif set(format_list) == {"album", "ep"}:
            return "ep"
        elif set(format_list) == {"compilation", "remixes"}:
            return "compilation"
        elif set(format_list) == {"compilation", "ep"}:
            return "ep"
        elif set(format_list) == {"album", "compilation"}:
            return "compilation"
        elif set(format_list) == {"ep", "remixes", "single"}:
            return "remixes"
        elif set(format_list) == {"album", "demo"}:
            return "demo"
        elif set(format_list) == {"album", "single"}:
            return "single"
        elif set(format_list) == {"ep", "single"}:
            return "single"
        elif set(format_list) == {'album', 'mixtape'}:
            return "mixtape"
        else:
            logger.warning(f"Unable to find dominant format in this list: {format_list}")
            return "unknown"

    @staticmethod
    def extract_songs_and_length(all_songs_raw, comment_number):

        if comment_number > -1:
            del all_songs_raw[-comment_number:]
        else:
            raise ValueError

        # removing <li> and </li>
        all_songs_without_html_li_tag = [song[4:-5] for song in all_songs_raw]

        # some character replacement
        all_songs_striped = [song.strip().replace('\xa0', ' ').replace('\u200e', ' ').replace("&amp;", "&")
                             for song in all_songs_without_html_li_tag if song.strip()]

        # build list of tuples containing song name and length. such as [(song_name, song_length), ...]
        all_songs_and_length_raw = [song.rsplit(" ", 1) for song in all_songs_striped]
        all_songs_and_length = [(element[0], element[1][1:-1]) for element in all_songs_and_length_raw]

        # in some case, song name is encapsulate in several strong tags. Here, removing theme
        all_songs_and_length_untaged = []
        for song in all_songs_and_length:
            if song[0].startswith("<strong>"):
                all_songs_and_length_untaged.append((song[0].replace("<strong>", "").replace("</strong>", ""), song[1]))
            else:
                all_songs_and_length_untaged.append((song[0], song[1]))

        # removing unwanted firsts characters
        all_songs_and_length_cleaned = []
        for song in all_songs_and_length_untaged:

            if song[0].startswith(" – "):
                if len(song[0]) > 3:
                    all_songs_and_length_cleaned.append((song[0][3:], song[1]))
            elif song[0].startswith("– "):
                if len(song[0]) > 2:
                    all_songs_and_length_cleaned.append((song[0][2:], song[1]))
            else:
                all_songs_and_length_cleaned.append((song[0], song[1]))

        return all_songs_and_length_cleaned

    @staticmethod
    def filter_label(label_extracted_string):
        start_marker = "[Label: "
        end_marker = " | "

        start_index = label_extracted_string.find(start_marker) + len(start_marker)
        end_index = label_extracted_string.find(end_marker)

        return label_extracted_string[start_index:end_index]


class SavingItemToDB:
    def __init__(self, engine):
        self._engine = engine
        self.session = None

    @classmethod
    def from_crawler(cls, crawler):
        db_url = crawler.settings.get("DATABASE")["db_url"]
        engine = get_engine(db_url)
        return cls(engine)

    def open_spider(self, spider):
        """
        This method is called when the spider is opened.
        """
        self.session = Session(self._engine)

    def close_spider(self, spider):
        if self.session is not None:
            self.session.close()

    @contextmanager
    def session_scope(self):
        """
        Provide a transactional scope around a series of operations.
        """
        try:
            yield self.session
            self.session.commit()
        except Exception as exc:
            self.session.rollback()
            logger.error(f"error occured during commit:\n{exc}")
        finally:
            self.session.close()

    def process_item(self, item, spider):

        with self.session_scope():
            release = self.create_release(item)

            for tag_name in item["tag_list"]:
                tag = self.get_or_create_tag(tag_name)
                release.tags.append(tag)

            for song_and_length in item["all_songs_and_length"]:
                self.create_song(song_and_length, release)

    def create_release(self, item):

        logger.info(f"data to insert: {item}")

        release_format = item["format"]

        existing_tag = self.session.query(Tag).filter_by(name=release_format).first()

        if existing_tag:
            release_format_id = existing_tag.id

        else:
            new_tag = self.get_or_create_tag(release_format)
            self.session.commit()
            release_format_id = new_tag.id

        release_data = {
            "artist_name": item["artist_name"],
            "release_name": item["release_name"],
            "release_creation_year": item["released_year"],
            "label_name": item["label_name"],
            "published_date": item["published_date"],
            "comment_number": item["comment_number"],
            "release_nodata_url": item["release_url"],
            "image_name": item["images"][0]["path"].split("/")[1],
            "format": release_format_id,
        }

        release = Release(**release_data)
        self.session.add(release)
        return release

    def get_or_create_tag(self, tag_name):

        existing_tag = self.session.query(Tag).filter_by(name=tag_name).first()

        if existing_tag:
            return existing_tag
        else:
            if tag_name in RELEASE_FORMATS:
                tag_type = 0  # format
            else:
                tag_type = 1  # style

            new_tag = Tag(name=tag_name, tag_type=tag_type)
            self.session.add(new_tag)

            return new_tag

    def create_song(self, song_name_and_length, release):
        song = Song(
            release_id=release.id,
            song_name=song_name_and_length[0],
            song_length=song_name_and_length[1]
        )
        self.session.add(song)
        return song









