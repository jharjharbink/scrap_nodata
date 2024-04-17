from sqlalchemy import create_engine


from scrap_nodata.db.tables import Base


def create_all_tables(engine):
    """
    Create all the tables inheriting from Base class declared in tables.py
    """
    Base.metadata.create_all(engine)


def get_engine(db_url):
    """
    Performs database connection using database settings from project_settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(db_url)