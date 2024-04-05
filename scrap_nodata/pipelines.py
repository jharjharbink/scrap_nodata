# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from datetime import datetime

from scrap_nodata.items import ReleaseItem
from logger import logger


def extract_info(all_text_elements):
    """
    all_text_elements can be like :
    s1 = "Daniel Avery – Wonderland / Running [2024]"
    s2 = "Daniel Avery – Wonderland / Running"
    s3 = "Daniel Avery / Wonderland - Running [2024]"
    s4 = "Daniel Avery / Wonderland - Running"

    the idea is to parse all of those string types to: "Daniel Avery", "Wonderland - Running", "2024"/None
    """

    all_text_elements_cleaned = all_text_elements.strip()

    # Extract artist_name and release_name from all_text_elements
    artist_release = all_text_elements_cleaned.split(' [')[0]

    if ' / ' in artist_release and ' – ' in artist_release:
        if artist_release.find(' / ') < artist_release.find(' – '):
            separator = ' / '
        else:
            separator = ' – '
    else:
        if ' / ' in artist_release:
            separator = ' / '
        else:
            separator = ' – '

    artist_name, release_name = artist_release.split(separator)

    # Extract released_year from all_text_elements_cleaned
    if all_text_elements_cleaned[-7:-5] == ' [' and all_text_elements_cleaned[-1] == ']':
        released_year = int(all_text_elements_cleaned[-5:-1])
    else:
        released_year = None

    return artist_name, release_name, released_year


def remove_format_from_tags(tags):
    format_tuple = (
        "remixes",
        "single",
        "ep",
        "album",
        "compilation",
        "Documentary",
        "demo",
        "dvd",
        "mixtape",
    )

    lower_cased_values = [item.lower() for item in tags]

    release_type_tags = [item for item in lower_cased_values if item in format_tuple]

    release_type = map_release_format(release_type_tags)

    tags = [item for item in lower_cased_values if item not in release_type]

    return tags, release_type


def map_release_format(format_list):
    """
    Sometimes, albums contains multiple tags, to describe their type of record, which are in conflict. this is all the
    combinations that I found and the priority
    """
    if len(format_list) == 0:  # if there is no format, there is no conflict.
        return None
    elif len(format_list) == 1:
        return format_list[0]  # if there is 1 format, there is no conflict.
    elif set(format_list) == {"album", "remixes"}:
        return "remixes"
    elif set(format_list) == {"ep", "remixes"}:
        return "remixes"
    elif set(format_list) == {"remixes", "Single"}:
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
    else:
        logger.info(f"Unable to find dominant format in this list: {format_list}")
        return None


def filter_label(label_extracted_string):
    start_marker = "[Label: "
    end_marker = " | "

    start_index = label_extracted_string.find(start_marker) + len(start_marker)
    end_index = label_extracted_string.find(end_marker)

    return label_extracted_string[start_index:end_index]


class PostProcessingPipeline:
    def process_item(self, item, spider):

        try:
            if 'artist_name_release_name_released_year' in item:
                artist_name, release_name, released_year = extract_info(item['artist_name_release_name_released_year'])
        except:
            logger.warning(f"unable to extract artist_name, release_name and released_year for item: {item.items()}")

        # Format published_date from 'Sep 08, 2023 ·' to '08/09/2023'

        try:
            if 'published_date' in item:
                try:
                    date_object = datetime.strptime(item['published_date'], '%b %d, %Y')
                    published_date = date_object.strftime('%d/%m/%Y')
                except ValueError:
                    published_date = None
                    logger.warning(f"unable to parse published_date from {published_date} to '%d/%m/%Y'")
        except:
            logger.warning(f"unable to parse published_date for item: {item.items()}")

        try:
            if 'tag_list' in item:
                tag_list, release_type = remove_format_from_tags(item['tag_list'])
        except:
            logger.warning(f"unable to parse tag_list for item: {item.items()}")

        # Format comment_number from 'No comments' to 0
        try:
            if 'comment_number' in item:
                try:
                    comment_number = item['comment_number'][0]
                    if comment_number[0].isdigit():
                        comment_number = int(comment_number.split(' ')[0])  # Extraire le nombre de commentaires
                    else:
                        comment_number = 0  # S'il n'y a pas de commentaires, mettre 0
                except ValueError:
                    comment_number = 0
        except:
            logger.warning(f"unable to parse comment_number for item: {item.items()}")

        try:
            if 'all_songs' in item:
                all_songs = [element.strip() for element in item['all_songs'] if element.strip()]
        except KeyError:
            logger.info(f"all_songs unavailable for this item: {item.items()}")

        try:
            if 'label_name' in item:
                label_name = filter_label(item['label_name'])
        except KeyError:
            logger.info(f"label_name unavailable for this item: {item.items()}")

        return ReleaseItem(
            artist_name=artist_name,
            release_name=release_name,
            released_year=released_year,
            published_date=published_date,
            tag_list=tag_list,
            release_type=release_type,
            comment_number=comment_number,
            release_image_url=item['release_image_url'],
            all_songs=all_songs,
            label_name=label_name,
            album_url=item['album_url'])


