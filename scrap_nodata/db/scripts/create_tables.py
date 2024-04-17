from scrap_nodata.db.scripts.usefull_functions import create_all_tables

db_url = ""  # db_url contains postgresql user and password

create_all_tables(db_url)
