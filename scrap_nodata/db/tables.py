from sqlalchemy import Table, Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Release(Base):
    __tablename__ = "release"

    id = Column(Integer, primary_key=True)
    artist_name = Column(String)
    release_name = Column(String)
    release_creation_year = Column(Integer)
    label_name = Column(String)
    published_date = Column(DateTime)
    comment_number = Column(Integer)
    release_nodata_url = Column(String)
    image_name = Column(String)
    format = Column(Integer, ForeignKey("tag.id"))

    tags = relationship("Tag", secondary="release_tag", back_populates="releases")
    songs = relationship("Song", back_populates="release")

    def __repr__(self):
        return (
            f"<Release(id={self.id}, "
            f"artist_name='{self.artist_name}', "
            f"release_name='{self.release_name}', "
            f"release_creation_year={self.release_creation_year}, "
            f"label='{self.label}', "
            f"format='{self.format}', "
            f"published_date={self.published_date}, "
            f"comment_number={self.comment_number}, "
            f"album_url='{self.album_url}', "
            f"image_urls='{self.image_urls}')>"
        )


class Song(Base):
    __tablename__ = "song"

    id = Column(Integer, primary_key=True)
    release_id = Column(Integer, ForeignKey("release.id"))
    song_name = Column(String)
    song_length = Column(String)

    release = relationship("Release", back_populates="songs")

    def __repr__(self):
        return (
            f"<Release(id={self.id}, "
            f"release_id={self.parent_id}, "
            f"song_name={self.song_name}"
            f"song_length={self.song_length})>"
        )


class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    tag_type = Column(Integer)

    releases = relationship("Release", secondary="release_tag", back_populates="tags")

    def __repr__(self):
        return (
            f"<Tag(id={self.id}, " 
            f"name={self.name}), " 
            f"tag_type={self.tag_type}>"
        )


release_tag = Table(
    "release_tag",
    Base.metadata,
    Column("release_id", Integer, ForeignKey("release.id")),
    Column("tag_id", Integer, ForeignKey("tag.id"))
)

