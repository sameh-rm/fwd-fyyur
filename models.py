from enum import unique
from sqlalchemy.orm import backref
from setup import db
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
genres = db.Table(
    "r_genres",
    db.Column('genres_id', db.Integer, db.ForeignKey(
        'genre.id'), nullable=False),
    db.Column('venue_id', db.Integer, db.ForeignKey(
        'venue.id'), nullable=True),
    db.Column('artist_id', db.Integer, db.ForeignKey(
        "artist.id"), nullable=True),
    db.Column('show_id', db.Integer, db.ForeignKey(
        "show.id"), nullable=True),
)


class Album(db.Model):
    __tablename__ = "album"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    image_link = db.Column(db.String(500), nullable=False)
    year = db.Column(db.Integer)
    songs = db.relationship(
        'Song', backref=db.backref("album", lazy='joined'))
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"))

    def __repr__(self):
        return f"{self.id} {self.name} {self.year} {self.artist_id}"


class Song(db.Model):
    __tablename__ = "song"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    # we might add an individual song
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.relationship('Genre', secondary=genres,
                             backref=db.backref("venues"))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship(
        'Show', backref=db.backref("venue", lazy='joined'))

    def __repr__(self):
        return f"<Venue {self.id} {self.name} {self.city} {self.state} {self.phone} {self.genres} {self.seeking_talent} {self.seeking_description}/>"


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.relationship(
        'Genre', secondary=genres, backref=db.backref("artist"))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship(
        'Show', backref=db.backref("artist", lazy='joined'))
    albums = db.relationship(
        "Album", backref=db.backref("artist", lazy="joined")
    )
    songs = db.relationship(
        "Song", backref=db.backref("artist", lazy="joined")
    )

    def __repr__(self):
        return f"<Artist {self.id} {self.name} {self.city} {self.state} {self.phone} {self.genres} {self.seeking_venue} {self.seeking_description}/>"


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Genre {self.id} {self.name}/>"


class Show (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # duration in minutes
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venue.id'), nullable=False)

    def __repr__(self):
        return f"<Show {self.id} {self.start_date} {self.artist.name} {self.venue.name}/>"
