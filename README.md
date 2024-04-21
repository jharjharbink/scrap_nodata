making a new scraper for the website nodata.tv

nodata.tv is a website that propose album to download severals times a week since 2008.
In this project, I scrap the album metadata listed below in order to make a better search engine than the one on website and data-analysis. I store those data in a postgresql database defined in database_schema.png, except for images which are stored in a AWS s3 bucket.

  - artist_name
  - release_name
  - release_creation_year
  - label_name
  - songs
  - songs length
  - tags (pop, jazz, dubstep...)
  - published_date
  - comment_number
  - release_nodata_url
  - image_name (stored on Amazon s3)
  - format (EP, Album, Mixtape...)


To run this project locally, you'll have to :
  - create an anaconda environment containing all the dependencies specified in requirements.txt file
  - get a default settings.py file from scrapy project and add the lines specified bellow
  - create a s3 bucket on AWS
  - download postgresql and create a database
  - in your conda environement, run the script located at scrap_nodata/db/scripts/create_tables.py with your db_url specified just like the one set in settings.py
  - in your conda environement, run the command "scrapy crawl nodataspider"

[Lines to add in settings.py file]

LOG_LEVEL = "ERROR"

BOT_NAME = "scrap_nodata"

SPIDER_MODULES = ["scrap_nodata.spiders"]
NEWSPIDER_MODULE = "scrap_nodata.spiders"

'twisted.internet.default.DefaultSelectorReactor'

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

ITEM_PIPELINES = {
    'scrap_nodata.pipelines.PostProcessingPipeline': 100,
    "scrap_nodata.pipelines.CustomImagesPipeline": 200,
    "scrap_nodata.pipelines.SavingItemToDB": 300
}

IMAGES_STORE_S3_ACL = "public-read"

IMAGES_STORE = "your_s3_bucket_location"

DATABASE = {
    "db_user": "your_user",
    "db_password": "your_password",
    "db_host": "your_host",
    "db_port": "your_port",
    "db_name": "your_db_name",
    "db_url": f"postgresql+psycopg2://your_user:your_password@your_host:your_port/your_db_name"  # don't forget to replace db_url elements with your db settings
}

AWS_ACCESS_KEY_ID = "your_access_key_id"
AWS_SECRET_ACCESS_KEY = "your_secret_access_key"
