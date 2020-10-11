from flask.app import Flask
from wtforms.fields.core import FieldList, FormField, IntegerField
from wtforms.fields.simple import TextAreaField
from fyyur_enums import GenresEnum, StatesEnum
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, IntegerField
from wtforms.validators import DataRequired, AnyOf, URL, ValidationError

from models import Venue, Genre, Artist, Show


class ShowForm(FlaskForm):
    # changed to selectField
    artist = SelectField(
        'artist',
        validators=[DataRequired()],
    )
    venue = SelectField(
        'venue',
        validators=[DataRequired()],
    )
    start_date = DateTimeField(
        'start_date',
        validators=[DataRequired()],
        format='%Y-%m-%d %H:%M',
        default=datetime.today()
    )
    duration = IntegerField(
        'duration',
        validators=[DataRequired()],
        default=30
    )


class SongForm(FlaskForm):
    name = StringField(
        'name',
        validators=[DataRequired()]
    )
    artist = SelectField(
        'artist',
        validators=[DataRequired()],
    )


class AlbumForm(FlaskForm):
    # changed to selectField
    name = StringField(
        'name',
        validators=[DataRequired()]
    )
    image_link = StringField(
        'image_link',
        validators=[URL(), DataRequired()]
    )
    year = IntegerField(
        'duration',
        default=2020,
        validators=[DataRequired()]
    )
    songs = TextAreaField("songs", description="Comma seprated values")


class VenueForm(FlaskForm):
    name = StringField(
        'name',
        validators=[DataRequired()]
    )
    city = StringField(
        'city',
        validators=[DataRequired()]
    )
    state = SelectField(
        'state',
        validators=[DataRequired()],
        # loop through the States Enum items to fill the choices array of the genres field
        choices=[
            (name.capitalize(), state.value)
            for name, state in StatesEnum.__members__.items()
        ]
    )
    address = StringField(
        'address',
        validators=[DataRequired()]
    )
    phone = StringField(
        'phone',
        validators=[DataRequired()],
    )
    image_link = StringField(
        'image_link',
        validators=[URL(), DataRequired()]
    )
    website = StringField(
        'website',
        validators=[URL()]
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres',
        validators=[DataRequired()],
        # loop through the Genres Enum items to fill the choices array of the genres field
        # choices=[
        #     (n.capitalize(), g.value,)
        #     for n, g in GenresEnum.__members__.items()
        # ]
    )
    facebook_link = StringField(
        'facebook_link',
        validators=[URL()]
    )
    seeking_talent = BooleanField(
        "seeking_talent", false_values=False, default=False)
    seeking_description = StringField("seeking_description",)


class ArtistForm(FlaskForm):
    name = StringField(
        'name',
        validators=[DataRequired()]
    )
    city = StringField(
        'city',
        validators=[DataRequired()]
    )
    state = SelectField(
        'state',
        validators=[DataRequired()],
        # loop through the States Enum items to fill the choices array of the genres field
        choices=[
            (name.capitalize(), state.value)
            for name, state in StatesEnum.__members__.items()
        ]
    )
    phone = StringField(
        'phone',
        validators=[DataRequired()]
    )
    image_link = StringField(
        'image_link',
        validators=[URL(), DataRequired()]
    )
    website = StringField(
        'website',
        validators=[URL()]
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres',
        validators=[DataRequired()],
        # loop through the Genres Enum items to fill the choices array of the genres field
        # choices=[
        #     (n.capitalize(), g.value, )
        #     for n, g in GenresEnum.__members__.items()
        # ]
        # a good practice for a Many To Many RelationShip

    )
    facebook_link = StringField(
        # TODO implement enum restriction ????
        'facebook_link', validators=[URL()]
    )
    seeking_venue = BooleanField(
        "seeking_venue", false_values=False, default=False)
    seeking_description = StringField("seeking_description",)


# TODO IMPLEMENT NEW ARTIST FlaskForm AND NEW SHOW FlaskForm
