#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from models import Album, Song
from operator import or_
import sys
from sqlalchemy.sql.sqltypes import JSON

from wtforms import form

from forms import *
from flask import Flask, render_template, request, Response, flash, redirect, url_for

import dateutil.parser
import babel
import logging
from logging import Formatter, FileHandler

from flask_wtf import Form
from setup import app, db
# from models import Venue, Genre, Artist, Show

from sqlalchemy import func
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


@app.route('/')
def index():
    data = {
        "venues": Venue.query.order_by(db.desc(Venue.id)).limit(10),
        "artists": Artist.query.order_by(db.desc(Artist.id)).limit(10),
    }
    return render_template('pages/home.html', recent=data)

#  Venues
#  ----------------------------------------------------------------


@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    areas = Venue.query.with_entities(
        Venue.city.distinct(), Venue.state).all()
    data = []

    for a in areas:
        area = {
            "city": a[0],
            "state": a[1],
            "venues": Venue.query.filter_by(state=a[1], city=a[0])
        }
        data.append(area)
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


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    data = Venue.query.get_or_404(venue_id)
    upcoming_shows = list(
        filter(lambda s: s.start_date > datetime.now(), data.shows))
    past_shows = list(
        filter(lambda s: s.start_date < datetime.now(), data.shows))
    upcoming_shows_count = len(upcoming_shows)
    past_shows_count = len(past_shows)
    shows_plan = {
        "upcoming_shows": upcoming_shows[:3],
        "upcoming_shows_count": upcoming_shows_count,
        "past_shows": past_shows[:3],
        "past_shows_count": past_shows_count,
    }

    return render_template('pages/show_venue.html', venue=data, plan=shows_plan,)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    form.genres.choices = [
        (genre.id, genre.name.capitalize())
        for genre in Genre.query.all()
    ]
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    data = None
    try:
        name = request.form.get('name')
        address = request.form.get('address')
        state = request.form.get('state')
        city = request.form.get('city')
        phone = request.form.get('phone')

        # mapping the genres to get the selected values by id
        # [*map(Genre.query.get_or_404, request.form.getlist('genres'))]
        genres = Genre.query.filter(
            Genre.id.in_(request.form.getlist('genres'))).all()
        facebook_link = request.form.get('facebook_link')
        website = request.form.get('website')
        image_link = request.form.get('image_link')
        # since the wtforms boolean field returns y if checked
        seeking_talent = request.form.get('seeking_talent') == 'y'
        seeking_description = request.form.get('seeking_description')

        data = Venue(
            name=name,
            address=address,
            state=state,
            city=city,
            phone=phone,
            genres=genres,
            facebook_link=facebook_link,
            website=website,
            image_link=image_link,
            seeking_talent=seeking_talent,
            seeking_description=seeking_description
        )

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
    item = Venue.query.get_or_404(venue_id)
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/confirm_delete.html', item_id=item.id, type="venues", name=item.name)


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
    return render_template('pages/home.html')

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
    return render_template('pages/home.html')


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

    upcoming_shows = list(
        filter(lambda s: s.start_date > datetime.now(), data.shows))
    past_shows = list(
        filter(lambda s: s.start_date < datetime.now(), data.shows))
    upcoming_shows_count = len(upcoming_shows)
    past_shows_count = len(past_shows)
    shows_plan = {
        "upcoming_shows": upcoming_shows[:3],
        "upcoming_shows_count": upcoming_shows_count,
        "past_shows": past_shows[:3],
        "past_shows_count": past_shows_count,
    }
    print(data.albums)
    return render_template(
        'pages/show_artist.html',
        artist=data,
        plan=shows_plan,
    )

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    form.genres. choices = [
        (genre.id, genre.name.capitalize())
        for genre in Genre.query.all()
    ]
    artist = {}
    try:
        artist = Artist.query.get_or_404(artist_id)

        form.genres.data = [genre.id for genre in artist.genres]
        form.genres.default = [genre.id for genre in artist.genres]
        form.process()

        form.state.data = artist.state
        form.name.data = artist.name
        form.city.data = artist.city
        form.image_link.data = artist.image_link
        form.facebook_link.data = artist.facebook_link
        form.website.data = artist.website
        form.phone.data = artist.phone
        form.seeking_venue.data = artist.seeking_venue
        form.seeking_description.data = artist.seeking_description
    except:
        flash(
            'this Artist is not existed', category='danger'
        )
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.get_or_404(artist_id)
    try:
        artist.name = request.form.get("name")
        artist.state = request.form.get("state")
        artist.city = request.form.get("city")
        artist.image_link = request.form.get("image_link")
        artist.facebook_link = request.form.get("facebook_link")
        artist.website = request.form.get("website")
        artist.phone = request.form.get("phone")
        artist.genres = Genre.query.filter(
            Genre.id.in_(request.form.get('genres')))
        # [*map(Genre.query.get_or_404, request.form.getlist('genres'))]
        artist.seeking_venue = request.form.get("seeking_venue") == "y"
        artist.seeking_description = request.form.get("seeking_description")
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
    return render_template("forms/new_album.html", form=form, artist=Artist.query.get_or_404(artist_id))


@app.route('/artist/albums/<artist_id>/create', methods=["POST"])
def create_album_submission(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    try:
        album_name = request.form.get("name")
        image_link = request.form.get("image_link")
        year = request.form.get("year")
        songs = request.form.get("songs")
        artist_songs = Song.query.filter(Song.artist_id == artist_id)
        songs_s = []
        for song in songs.split(','):
            if artist_songs.filter(Song.name == song).count() == 0:
                songs_s.append(Song(name=song, artist_id=artist_id))
            else:
                flash("this song is already existed")
        album = Album(
            name=album_name,
            image_link=image_link,
            year=year,
            songs=songs_s,
            artist_id=artist_id
        )
        db.session.add(album)
        db.session.commit()
        flash(
            'Album ' + album_name +
            ' was successfully listed!', category='info')
    except:
        print(sys.exc_info())
        flash(
            'An error occurred. Album ' +
            album_name + ' could not be listed.', category='danger'
        )
        print(sys.exc_info())
        db.session.rollback()
    return redirect(url_for("show_artist", artist_id=artist.id))


@app.route('/artist/albums/<album_id>/edit')
def edit_album(album_id):
    form = AlbumForm()
    album = Album.query.get_or_404(album_id)
    artist_id = album.artist_id

    form.name.data = album.name
    form.songs.data = ", ".join([s.name for s in album.songs])
    form.image_link.data = album.image_link
    form.year.data = album.year
    return render_template("forms/edit_album.html", form=form, album_id=album_id, artist=Artist.query.get_or_404(artist_id))


@app.route('/artist/albums/<album_id>/edit', methods=["POST"])
def edit_album_submission(album_id):
    album = Album.query.get_or_404(album_id)
    artist_id = album.artist.id
    artist = Artist.query.get_or_404(album.artist_id)
    try:
        album.name = request.form.get("name")
        album.image_link = request.form.get("image_link")
        album.year = request.form.get("year")
        songs = request.form.get("songs")
        Song.query.filter(
            Song.album_id == album_id).delete()
        songs_list = []
        for song in songs.split(','):
            songs_list.append(Song(name=song, artist_id=artist_id))
        album.songs = songs_list
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
    return redirect(url_for("show_artist", artist_id=artist.id))


@app.route('/shows/<album_id>/delete', methods=["GET"])
def delete_album(album_id):
    album = Album.query.get_or_404(album_id)
    return render_template('pages/confirm_delete_album.html', album=album)


@app.route('/shows/<album_id>/confirm_delete', methods=["GET"])
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
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist.id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    form.genres.choices = [
        (genre.id, genre.name.capitalize())
        for genre in Genre.query.all()
    ]

    venue = {}
    try:
        venue = Venue.query.get_or_404(venue_id)

        form.genres.data = [genre.id for genre in venue.genres]
        form.genres.default = [genre.id for genre in venue.genres]

        form.process()
        form.state.data = venue.state
        form.name.data = venue.name
        form.city.data = venue.city
        form.address.data = venue.address
        form.image_link.data = venue.image_link
        form.facebook_link.data = venue.facebook_link
        form.website.data = venue.website
        form.phone.data = venue.phone
        form.seeking_talent.data = venue.seeking_talent
        form.seeking_description.data = venue.seeking_description
    except:
        flash(
            'this venue is not existed', category='danger'
        )
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.get_or_404(venue_id)
    try:
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
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


# @ app.route('/artist_shows/<artist_id>')
# def get_artist_shows_json(artist_id):
#     artist = Artist.query.get_or_404(artist_id)
#     data = map(lambda show: {
#         "venue_id": show.venue.id,
#         "venue_name": show.venue.name,
#         "artist_id": show.artist.id,
#         "artist_name": show.artist.name,
#         "start_date": str(show.start_date),
#         "end_time": str(show.end_time),
#         "duration": show.duration,
#         "id": show.id
#     }, artist.shows)
#     return json.dumps({
#         "shows": list(data)
#     })


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
    try:
        # retrieve the form data
        name = request.form.get('name')
        state = request.form.get('state')
        city = request.form.get('city')
        phone = request.form.get('phone')

        # mapping the genres to get the selected values
        genres = Genre.query.filter(
            Genre.id.in_(request.form.getlist('genres'))).all()
        facebook_link = request.form.get('facebook_link')
        website = request.form.get('website')
        image_link = request.form.get('image_link')
        # since the wtforms boolean field returns y if checked
        seeking_venue = request.form.get('seeking_venue') == 'y'
        seeking_description = request.form.get('seeking_description')

        artist = Artist(
            name=name,
            state=state,
            city=city,
            phone=phone,
            genres=genres,
            facebook_link=facebook_link,
            website=website,
            image_link=image_link,
            seeking_venue=seeking_venue,
            seeking_description=seeking_description,
        )

        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] +
              ' was successfully listed!', category='info')
    except:
        flash(
            'An error occurred. Artist ' +
            request.form['name'] + ' could not be listed.', category='danger'
        )
        db.session.rollback()
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


def init_show_form():
    form = ShowForm()

    form.artist.choices = [
        (artist.id, artist.name.capitalize())
        for artist in Artist.query.order_by('id').all()
    ]
    form.venue.choices = [
        (venue.id, venue.name.capitalize())
        for venue in Venue.query.order_by('id').all()
    ]
    return form


@app.route('/shows/<show_id>/delete', methods=["GET"])
def delete_show(show_id):
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
    return render_template('pages/home.html')


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


def save_show(artist,
              venue,
              start_date,
              duration,
              end_time,):
    show = Show(
        artist=artist,
        venue=venue,
        start_date=start_date,
        duration=duration,
        end_time=end_time
    )
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
    form = init_show_form()

    return render_template('forms/new_show.html', form=form)
    # return form


@app.route('/shows/create/<artist_id>')
def artist_create_show(artist_id):
    # renders form. do not touch.
    form = init_show_form()
    form.artist.default = artist_id
    form.process()
    return render_template('forms/new_show.html', form=form)
    # return form


def create_new_show():
    try:
        form = request.form
        venue = Venue.query.get_or_404(form.get('venue'))
        artist = Artist.query.get_or_404(form.get('artist'))
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
            if artist_is_available and venue_is_available:
                save_show(artist,
                          venue,
                          start_date,
                          duration,
                          end_time,)
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

    except:
        print(sys.exc_info())
        flash('An error occurred. Show could not be listed.', category='danger')
        db.session.rollback()
    finally:
        db.session.close()


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    show = {}
    create_new_show()

    return redirect(url_for("index"))


@app.route('/shows/create/<artist_id>', methods=['POST'])
def artist_create_show_submission(artist_id):
    show = {}
    create_new_show()
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
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
