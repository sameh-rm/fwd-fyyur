#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
from models import Album, Song
from operator import or_
from forms import *
from flask import (render_template, request, flash, redirect, url_for)

import dateutil.parser
import babel
import logging
from logging import Formatter, FileHandler

from setup import app, db
# from models import Venue, Genre, Artist, Show

from sqlalchemy import func
from sqlalchemy.orm import load_only
from flask_moment import Moment
from flask_migrate import Migrate
from datetime import timedelta
# TODO: connect to a local postgresql database


moment = Moment(app)
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


def get_recent_data():
    return {
        "venues": Venue.query.order_by(db.desc(Venue.id)).limit(10),
        "artists": Artist.query.order_by(db.desc(Artist.id)).limit(10),
    }


@app.route('/')
def index():

    return render_template('pages/home.html', recent=get_recent_data())

#  Venues
#  ----------------------------------------------------------------


@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    areas = Venue.query.with_entities(
        Venue.city.distinct(), Venue.state).all()
    data = []
    print(areas)
    for city, state in areas:
        area = {
            "city": city,
            "state": state,
            "venues": Venue.query.filter_by(city=city, state=state)
        }
        data.append(area)
    print(data)
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_val = request.form.get("search_term").lower()
    data = Venue.query.filter(func.lower(Venue.name).like(f'%{search_val}%'))

    response = {
        "count": data.count(),
        "data": data
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


def get_shows_formated(data):
    """ data: instance of Artist or Venue """
    upcoming_shows = data.shows.filter(
        Show.start_date > datetime.now())
    past_shows = data.shows.filter(
        Show.start_date < datetime.now())
    upcoming_shows_count = upcoming_shows.count()
    past_shows_count = past_shows.count()
    return {
        "upcoming_shows": upcoming_shows.limit(3).all(),
        "upcoming_shows_count": upcoming_shows_count,
        "past_shows": past_shows.limit(3).all(),
        "past_shows_count": past_shows_count,
    }


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    data = Venue.query.get_or_404(venue_id)
    return render_template('pages/show_venue.html', venue=data, plan=get_shows_formated(data),)

#  Create Venue
#  ----------------------------------------------------------------


def get_choices(data_model):
    """
    data_model: db.Model (Artist,Venue,Genre,...etc)
    """
    return [
        (item.id, item.name.capitalize())
        for item in data_model.query.all()
    ]


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    form.genres.choices = Genre.get_choices()
    return render_template('forms/new_venue.html', form=form)


def create_new_instance(data_model):
    """
        data_model: Artist or Venue \n
        Creates a new instance of Artist or Venue 
    """
    name = request.form.get('name')
    state = request.form.get('state')
    city = request.form.get('city')
    phone = request.form.get('phone')
    genres = Genre.query.filter(
        Genre.id.in_(request.form.getlist('genres'))).all()
    facebook_link = request.form.get('facebook_link')
    website = request.form.get('website')
    image_link = request.form.get('image_link')
    # since the wtforms boolean field returns y if checked
    seeking_description = request.form.get('seeking_description')
    data = data_model(
        name=name,
        state=state,
        city=city,
        phone=phone,
        genres=genres,
        facebook_link=facebook_link,
        website=website,
        image_link=image_link,
        seeking_description=seeking_description
    )

    if hasattr(data_model, "seeking_talent"):
        data.seeking_talent = request.form.get('seeking_talent') == 'y'
        data.address = request.form.get('address')
    else:
        data.seeking_venue = request.form.get('seeking_venue') == 'y'

    return data


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    data = None
    try:
        data = create_new_instance(Venue)
        db.session.add(data)
        db.session.commit()
        flash('Venue ' + request.form['name'] +
              ' was successfully listed!', category='info')
    except:
        print(sys.exc_info())
        flash(
            'An error occurred. Venue ' +
            request.form['name'] + ' could not be listed.', category='danger'
        )
        db.session.rollback()
        # filling venue form
        form = VenueForm()
        fill_form_with_data(form, data)
        return render_template("forms/new_venue.html", form=form)
    finally:
        db.session.close()
    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return redirect(url_for("index"))


@app.route('/venues/<venue_id>/delete', methods=["GET"])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    venue = Venue.query.get_or_404(venue_id)
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/confirm_delete.html', venue=venue)


@app.route('/venues/<venue_id>/confirm_delete', methods=["GET"])
def confirm_delete_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    try:
        db.session.delete(venue)
        db.session.commit()
        flash('Venue ' + venue.name +
              ' was successfully deleted!', category='info')
    except:
        flash(
            'An error occurred. Venue ' +
            venue.name + ' could not be deleted.', category='danger'
        )
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for("index", recent=get_recent_data))

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/<artist_id>/delete', methods=["GET"])
def delete_artist(artist_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    artist = Artist.query.get_or_404(artist_id)
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/confirm_delete_artist.html', artist=artist)


@app.route('/artists/<artist_id>/confirm_delete', methods=["GET"])
def confirm_delete_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    try:
        db.session.delete(artist)
        db.session.commit()
        flash(
            'Artist ' + artist.name +
            ' was successfully deleted!', category='info'
        )
    except:
        flash(
            'An error occurred. Artist ' +
            artist.name + ' could not be deleted.', category='danger'
        )
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for("index", recent=get_recent_data))


@app.route('/artists/search_json', methods=["POST"])
def search_json_artist():
    try:
        search_term = request.get_json()["search_term"].lower()
        print(search_term)
        found_artists = Artist.query.filter(func.lower(
            Artist.name).like(f'%{search_term}%')).all()

        result = map(lambda artist: {
            "name": artist.name,
            "city": artist.city,
            "image_link": artist.image_link,
            "absoluteURL": url_for("show_artist", artist_id=artist.id)
        }, found_artists)
        return json.dumps({"data": [*result]})
    except:
        print(sys.exc_info())
        return json.dumps({"message": sys.exc_info(), "type": "error"})


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    # SELECT * FROM artist where artist.name like %'Search'%
    search_val = request.form.get("search_term").lower()
    data = Artist.query.filter(func.lower(Artist.name).like(f'%{search_val}%'))

    response = {
        "count": data.count(),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    data = Artist.query.get_or_404(artist_id)
    return render_template(
        'pages/show_artist.html',
        artist=data,
        plan=get_shows_formated(data),
    )

#  Update
#  ----------------------------------------------------------------


def fill_form_with_data(form, instance):
    """
    filling VenueForm or ArtistForm with the passed instance
    form : VenueForm or ArtistForm
    instance : is an instance of Artist or Venue
    """
    form.genres.choices = Genre.get_choices()
    form.genres.data = [genre.id for genre in instance.genres]
    form.genres.default = [genre.id for genre in instance.genres]
    form.process()
    if isinstance(instance, Venue):
        form.address.data = instance.address
        form.seeking_talent.data = instance.seeking_talent
    else:
        form.seeking_venue.data = instance.seeking_venue
    form.state.data = instance.state
    form.name.data = instance.name
    form.city.data = instance.city
    form.image_link.data = instance.image_link
    form.facebook_link.data = instance.facebook_link
    form.website.data = instance.website
    form.phone.data = instance.phone
    form.seeking_description.data = instance.seeking_description


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = {}
    try:
        artist = Artist.query.get_or_404(artist_id)
        fill_form_with_data(form, artist)
    except:
        flash(
            'this Artist is not existed', category='danger'
        )
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


def update_artist(artist):
    artist.name = request.form.get("name")
    artist.state = request.form.get("state")
    artist.city = request.form.get("city")
    artist.image_link = request.form.get("image_link")
    artist.facebook_link = request.form.get("facebook_link")
    artist.website = request.form.get("website")
    artist.phone = request.form.get("phone")
    artist.genres = Genre.query.filter(
        Genre.id.in_(request.form.getlist('genres')))
    artist.seeking_venue = request.form.get("seeking_venue") == "y"
    artist.seeking_description = request.form.get("seeking_description")


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    artist = Artist.query.get_or_404(artist_id)
    try:
        update_artist(artist)
        db.session.commit()
        flash(
            'Artist ' + artist.name +
            ' was successfully updated!', category='info')
    except:
        print(sys.exc_info())
        flash(
            'An error occurred. Artist ' +
            artist.name + ' could not be updated.', category='danger'
        )
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/artist/albums/<artist_id>/create')
def create_album(artist_id):
    form = AlbumForm()
    artist = Artist.query.get_or_404(artist_id)
    return render_template("forms/new_album.html", form=form, artist=artist)


def create_new_album(artist):
    album_name = request.form.get("name")
    image_link = request.form.get("image_link")
    year = request.form.get("year")
    songs = request.form.get("songs")
    artist_songs = Song.query.filter(Song.artist_id == artist.id)
    songs_s = []
    for song in songs.split(','):
        if artist_songs.filter(Song.name == song).count() == 0:
            songs_s.append(Song(name=song, artist_id=artist.id))
        else:
            flash("this song is already existed")
    album = Album(
        name=album_name,
        image_link=image_link,
        year=year,
        songs=songs_s,
        artist_id=artist.id
    )
    return album


def fill_album_form(form, album):
    form.name.data = album.name
    form.songs.data = ", ".join([s.name for s in album.songs])
    form.image_link.data = album.image_link
    form.year.data = album.year


@app.route('/artist/albums/<artist_id>/create', methods=["POST"])
def create_album_submission(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    album = {}
    try:
        album = create_new_album(artist)
        db.session.add(album)
        db.session.commit()
        flash(
            'Album ' + album.name +
            ' was successfully listed!', category='info')
    except:
        print(sys.exc_info())
        flash(
            'An error occurred. Album ' +
            album.name + ' could not be listed.', category='danger'
        )
        print(sys.exc_info())
        db.session.rollback()
        form = AlbumForm()
        fill_album_form(form, album)

        return render_template("forms/new_album.html", form=form, artist=artist)
    finally:
        db.session.close()

    return redirect(url_for("show_artist", artist_id=artist.id))


@app.route('/artist/albums/<album_id>/edit')
def edit_album(album_id):
    form = AlbumForm()
    album = Album.query.get_or_404(album_id)
    fill_album_form(form, album)
    return render_template("forms/edit_album.html", form=form, album_id=album_id, artist=Artist.query.get_or_404(album.artist_id))


def update_album(album):
    album.name = request.form.get("name")
    album.image_link = request.form.get("image_link")
    album.year = request.form.get("year")
    songs = request.form.get("songs")
    Song.query.filter(
        Song.album_id == album.id).delete()
    songs_list = []
    for song in songs.split(','):
        songs_list.append(Song(name=song, artist_id=album.artist_id))
    album.songs = songs_list


@app.route('/artist/albums/<album_id>/edit', methods=["POST"])
def edit_album_submission(album_id):
    album = Album.query.get_or_404(album_id)
    artist = Artist.query.get_or_404(album.artist_id)
    try:
        update_album(album)
        db.session.commit()
        flash(
            'Album ' + album.name +
            ' was successfully Updated!', category='info')
    except:
        print(sys.exc_info())
        flash(
            'An error occurred. Album ' +
            album.name + ' could not be Updated.', category='danger'
        )
        print(sys.exc_info())
        db.session.rollback()
        form = AlbumForm()
        fill_album_form(form, album)
        return render_template("forms/edit_album.html", form=form, album_id=album_id, artist=Artist.query.get_or_404(album.artist_id))
    finally:
        db.session.close()

    return redirect(url_for("show_artist", artist_id=artist.id))


@app.route('/albums/<album_id>/delete', methods=["GET"])
def delete_album(album_id):
    album = Album.query.get_or_404(album_id)
    return render_template('pages/confirm_delete_album.html', album=album)


@app.route('/albums/<album_id>/confirm_delete', methods=["GET"])
def confirm_delete_album(album_id):
    album = Album.query.get_or_404(album_id)
    artist = album.artist
    try:
        db.session.delete(album)
        db.session.commit()
        flash('The Album of ' + album.name +
              ' was successfully deleted!', category='info')
    except:
        flash(
            'An error occurred. Album ' +
            album.name + ' could not be deleted.', category='danger'
        )
        db.session.rollback()
        return render_template('pages/confirm_delete_album.html', album=album)
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist.id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = {}
    try:
        venue = Venue.query.get_or_404(venue_id)
        fill_form_with_data(form, venue)
    except:
        flash(
            'this venue is not existed', category='danger'
        )
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


def update_venue(venue):
    venue.name = request.form.get("name")
    venue.state = request.form.get("state")
    venue.city = request.form.get("city")
    venue.address = request.form.get("address")
    venue.image_link = request.form.get("image_link")
    venue.facebook_link = request.form.get("facebook_link")
    venue.website = request.form.get("website")
    venue.phone = request.form.get("phone")
    venue.genres = Genre.query.filter(
        Genre.id.in_(request.form.getlist('genres'))).all()
    venue.seeking_talent = request.form.get("seeking_talent") == "y"
    venue.seeking_description = request.form.get("seeking_description")


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    # get venue from database
    venue = Venue.query.get_or_404(venue_id)
    try:
        # update venues attributes
        update_venue(venue)
        # commit session transactions
        db.session.commit()
        flash(
            'Venue ' + venue.name +
            ' was successfully updated!', category='info')
    except:
        print(sys.exc_info())
        flash(
            'An error occurred. Venue ' +
            venue.name + ' could not be updated.', category='danger'
        )
        db.session.rollback()
        form = VenueForm()
        fill_form_with_data(form, venue)
        return render_template('forms/edit_venue.html', form=form, venue=venue)
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    form.genres. choices = [
        (genre.id, genre.name.capitalize())
        for genre in Genre.query.all()
    ]
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    data = {}
    try:
        data = create_new_instance(Artist)
        db.session.add(data)
        db.session.commit()
        flash('Artist ' + request.form['name'] +
              ' was successfully listed!', category='info')
    except:
        flash(
            'An error occurred. Artist ' +
            request.form['name'] + ' could not be listed.', category='danger'
        )
        db.session.rollback()
        form = ArtistForm()
        fill_form_with_data(form, data)
        return render_template("forms/new_venue.html", form=form)
    finally:
        db.session.close()

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return redirect(url_for("index"))


#  Shows
#  ----------------------------------------------------------------

@ app.route('/shows')
def shows():
    # mapping the Show data using lambda experssion to return the right data form
    data = map(lambda show: {
        "venue_id": show.venue.id,
        "venue_name": show.venue.name,
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_date,
        "id": show.id
    }, Show.query.limit(9).all())
    return render_template('pages/shows.html', shows=data)


@ app.route('/shows/search', methods=['POST'])
def search_shows():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get("search_term").lower()
    data = Show.query.join('artist').join('venue').filter(
        or_(
            func.lower(Artist.name).like(f'%{search_term}%'),
            func.lower(Venue.name).like(f'%{search_term}%')
        )
    ).distinct(Show.id).all()
    response = {
        "count": len(data),
        "data": data,
    }

    return render_template('pages/show.html', results=response, search_term=request.form.get('search_term', ''))


def show_form():
    form = ShowForm()
    form.artist.choices = Artist.get_ordered_choices("id")
    form.venue.choices = Venue.get_ordered_choices("id")
    return form


@app.route('/shows/<show_id>/delete', methods=["GET"])
def delete_show(show_id):
    print(Show.query.first())
    show = Show.query.get_or_404(show_id)
    return render_template('pages/confirm_delete_show.html', show=show)


@app.route('/shows/<show_id>/confirm_delete', methods=["GET"])
def confirm_delete_show(show_id):
    show = Show.query.get_or_404(show_id)
    artist = show.artist
    try:
        db.session.delete(show)
        db.session.commit()
        flash('The show of ' + artist.name +
              ' was successfully deleted!', category='info')
    except:
        flash(
            'An error occurred. Show ' +
            artist.name + ' could not be deleted.', category='danger'
        )
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for("index", recent=get_recent_data))


@ app.route('/shows/<int:show_id>/edit', methods=['GET'])
def edit_show(show_id):
    show = {}
    form = ShowForm()

    try:
        show = Show.query.get_or_404(show_id)
        form.venue.default = show.venue.id
        form.artist.default = show.artist.id
        form.process()
        form.artist.choices = [
            (artist.id, artist.name.capitalize())
            for artist in Artist.query.order_by('id').all()
        ]
        form.venue.choices = [
            (venue.id, venue.name.capitalize())
            for venue in Venue.query.order_by('id').all()
        ]
        form.start_date.data = show.start_date
    except:
        flash(
            'this Show is not existed', category='danger'
        )
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_show.html', form=form, show=show)


@ app.route('/shows/<int:show_id>/edit', methods=['POST'])
def edit_show_submission(show_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    show = Show.query.get_or_404(show_id)
    try:
        show.artist = Artist.query.get_or_404(request.form.get("artist"))
        show.venue = Venue.query.get_or_404(request.form.get("venue"))
        show.start_date = request.form.get("start_date")
        db.session.commit()
        flash(
            'Show ' + show.artist.name +
            ' was successfully updated!', category='info')
    except:
        print(sys.exc_info())
        flash(
            'An error occurred. Show ' +
            show.artist.name + ' could not be updated.', category='danger'
        )
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('shows'))


def save_show(artist, venue, start_date, duration, end_time):
    show = Show(artist=artist, venue=venue, start_date=start_date,
                duration=duration, end_time=end_time)
    db.session.add(show)
    db.session.commit()
    flash(
        'Show ' + show.artist.name +
        ' was successfully listed!',
        category='success')
    return {
        "artist": {"name": show.artist.name, "id": show.artist.id},
        "venue": {"name": show.venue.name, "id": show.venue.id},
        "start_date": str(show.start_date),
        "end_time": str(show.end_time),
        "duration": show.duration,
    }


@app.route('/shows/create/', )
def create_show():
    # renders form. do not touch.
    form = show_form()
    return render_template('forms/new_show.html', form=form)
    # return form


@app.route('/shows/create/<artist_id>')
def artist_create_show(artist_id):
    # renders form. do not touch.
    form = show_form()
    form.artist.default = artist_id
    form.process()
    return render_template('forms/new_show.html', form=form)


def create_new_show(form, venue, artist):
    check_availablity = artist.seeking_venue and venue.seeking_talent
    if check_availablity:
        # artist.shows where end_time > date.now and
        start_date = datetime.strptime(
            form.get('start_date'), '%Y-%m-%d %H:%M')
        duration = form.get('duration')
        end_time = start_date + timedelta(minutes=float(duration))
        artist_is_available = Show.query.filter(
            Show.artist_id == artist.id).filter(Show.end_time > start_date).count() == 0
        venue_is_available = Show.query.filter(
            Show.venue_id == venue.id).filter(Show.end_time > start_date).count() == 0
        # check if the artist has no shows at the same time
        if artist_is_available and venue_is_available:
            return save_show(artist, venue, start_date, duration, end_time)
        elif not artist_is_available:
            flash(
                'This Artist is not Availble for a booking!',
                category='warning'
            )
        else:
            flash(
                f'This Venue is not Availble for a booking till {end_time}!',
                category='warning'
            )
    elif not venue.seeking_talent:
        flash(
            'This Venue is not looking for a talent!',
            category='warning'
        )
    else:
        flash(
            'This Artist is not looking for a venue!',
            category='warning'
        )
    return render_template('forms/new_show.html', form=show_form())


@app.route('/shows/create/', methods=['POST'])
def create_show_submission(artist_id):
    try:
        form = request.form
        venue = Venue.query.get_or_404(form.get('venue'))
        artist = Artist.query.get_or_404(form.get('artist'))
        create_new_show(form, venue, artist)
    except:
        print(sys.exc_info())
        flash('An error occurred. Show could not be listed.', category='danger')
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for("index"))


@app.route('/shows/create/<artist_id>', methods=['POST'])
def artist_create_show_submission(artist_id):
    try:
        form = request.form
        venue = Venue.query.get_or_404(form.get('venue'))
        artist = Artist.query.get_or_404(artist_id)
        create_new_show(form, venue, artist)
    except:
        print(sys.exc_info())
        flash('An error occurred. Show could not be listed.', category='danger')
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for("index"))


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True,port=8000)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
