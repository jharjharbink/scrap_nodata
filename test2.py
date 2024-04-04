def remove_format_from_tags(my_list):
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

    lower_cased_values = [item.lower() for item in my_list]

    excluded_values = [item for item in my_list if item in format_tuple]

    tags = [item for item in lower_cased_values if item not in excluded_values]

    return tags, excluded_values


def map_release_format(format_list):
    """
    Sometimes, albums contains multiple tags, to describe their type of record, which are in conflict. this is all the
    combinations that I found and the priority
    """
    if (
        len(format_list) < 2
    ):  # if there is no format or one format, there is no conflict.
        return format_list
    elif format_list == ["album", "remixes"]:
        return "remixes"
    elif format_list == ["ep", "remixes"]:
        return "remixes"
    elif format_list == ["remixes", "Single"]:
        return "remixes"
    elif format_list == ["album", "ep"]:
        return "ep"
    elif format_list == ["compilation", "remixes"]:
        return "compilation"
    elif format_list == ["compilation", "ep"]:
        return "ep"
    elif format_list == ["album", "compilation"]:
        return "compilation"
    elif format_list == ["ep", "remixes", "single"]:
        return "remixes"
    elif format_list == ["album", "demo"]:
        return "demo"
    elif format_list == ["album", "single"]:
        return "single"
    elif format_list == ["ep", "single"]:
        return "single"
    else:
        return None

tags = ['album',
              'ambient',
              'dub',
              'electronic',
              'experimental',
              'techno']

tag_list, release_type_tags = remove_format_from_tags(tags)
release_type = map_release_format(release_type_tags)

print(tag_list)
print(release_type_tags)

