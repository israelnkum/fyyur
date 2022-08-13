# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import logging
from logging import Formatter, FileHandler

import babel
import dateutil.parser
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from sqlalchemy import func

from forms import *
from models import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

now = datetime.now()


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


def count_venue_shows(venue_id, upcoming=True):
    if upcoming:
        return Show.query.filter_by(venue_id=venue_id).filter(Show.start_date_time > now).count()
    return Show.query.filter_by(venue_id=venue_id).filter(Show.start_date_time < now).count()


def count_artist_shows(artist_id, upcoming=True):
    if upcoming:
        return Show.query.filter_by(artist_id=artist_id).filter(Show.start_date_time > now).count()
    return Show.query.filter_by(artist_id=artist_id).filter(Show.start_date_time < now).count()


def get_artists_shows(artist_id, upcoming=True):
    if upcoming:
        all_shows = db.session.query(Show, Venue).filter_by(artist_id=artist_id).outerjoin(Venue,
                                                                                           Show.venue_id == Venue.id).filter(
            Show.start_date_time > now).all()
    else:
        all_shows = db.session.query(Show, Venue).filter_by(artist_id=artist_id).outerjoin(Venue,
                                                                                           Show.venue_id == Venue.id).filter(
            Show.start_date_time < now).all()

    data = []
    for item in all_shows:
        data.append({
            "venue_id": item.Venue.id,
            "venue_name": item.Venue.name,
            "venue_image_link": item.Venue.image_link,
            "start_time": str(item['Show'].start_date_time)
        })

    res = dict()
    res['total'] = len(data)
    res['data'] = data

    return res


def get_venue_shows(venue_id, upcoming=True):
    if upcoming:
        all_shows = db.session.query(Show, Artist, Venue).join(Artist, Venue).filter_by(id=venue_id).filter(
            Show.start_date_time > now).all()
    else:
        all_shows = db.session.query(Show, Artist, Venue).join(Artist, Venue).filter_by(id=venue_id).filter(
            Show.start_date_time < now).all()

    data = []
    for item in all_shows:
        data.append({
            "artist_id": item['Artist'].id,
            "artist_name": item['Artist'].name,
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": str(item['Show'].start_date_time),
        })

    res = dict()
    res['total'] = len(data)
    res['data'] = data

    return res


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    cities = db.session.query(Venue.city, func.count(Venue.city).label("total_counts")) \
        .outerjoin(Show).group_by(Venue.city).all()

    data = []
    for city in cities:
        city_data = {
            "city": city[0],
            "state": "",
            "venues": []
        }
        cities = Venue.query.filter_by(city=city[0]).all()
        for ci in cities:
            city_data["state"] = ci.state
            city_data["venues"].append({
                "id": ci.id,
                "name": ci.name,
                "num_upcoming_shows": count_venue_shows(ci.id)
            })
        data.append(city_data)

    # data = [{
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "venues": [{
    #         "id": 1,
    #         "name": "The Musical Hop",
    #         "num_upcoming_shows": 0,
    #     }, {
    #         "id": 3,
    #         "name": "Park Square Live Music & Coffee",
    #         "num_upcoming_shows": 1,
    #     }]
    # }, {
    #     "city": "New York",
    #     "state": "NY",
    #     "venues": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }]
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    results = Venue.query.filter(Venue.name.ilike("%" + search_term + "%")).all()
    data = []
    response = {
        "count": len(results),
        "data": data
    }

    for result in results:
        data.append({
            "id": result.id,
            "name": result.name,
            "num_upcoming_shows": count_venue_shows(result.id),
        })

    return render_template('pages/search_venues.html', results=response, search_term=search_term)


def single_venue(venue_id, editing=False):
    venue = Venue.query.filter_by(id=venue_id).outerjoin(Venue_Genre, Venue.id == Venue_Genre.venue_id).first()

    gen = []
    if len(venue.genres) > 0:
        for ge in venue.genres:
            gen.append(ge.genre)

    if editing:
        return {
            "id": venue.id,
            "name": venue.name,
            "genres": gen,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website_link,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "image_link": venue.image_link,
        }

    past_shows = get_venue_shows(venue_id, upcoming=False)
    upcoming_shows = get_venue_shows(venue_id)
    return {
        "id": venue.id,
        "name": venue.name,
        "genres": gen,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "image_link": venue.image_link,
        "past_shows": past_shows['data'],
        "upcoming_shows": upcoming_shows['data'],
        "past_shows_count": past_shows['total'],
        "upcoming_shows_count": upcoming_shows['total']
    }


@app.route('/shows/search', methods=['POST'])
def search_shows():
    search_term = request.form.get('search_term', '')
    artist_results = db.session.query(Show, Artist).join(Artist).filter(
        Artist.name.ilike("%" + search_term + "%")).all()
    artist_data = []
    artist_response = {
        "count": len(artist_results),
        "data": artist_data
    }

    for result in artist_results:
        artist_data.append({
            "id": result.Artist.id,
            "name": result.Artist.name,
            "num_upcoming_shows": count_venue_shows(result.Artist.id),
        })

    venue_results = db.session.query(Show, Venue).join(Venue).filter(
        Venue.name.ilike("%" + search_term + "%")).all()

    venue_data = []
    venue_response = {
        "count": len(venue_results),
        "data": venue_data
    }

    for result in venue_results:
        venue_data.append({
            "id": result.Venue.id,
            "name": result.Venue.name,
            "num_upcoming_shows": count_venue_shows(result.Venue.id),
        })

    return render_template('pages/show.html', artists=artist_response, venues=venue_response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    data = single_venue(venue_id)
    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    data = {}
    try:
        name = request.form.get("name")
        city = request.form.get("city")
        state = request.form.get("state")
        address = request.form.get("address")
        phone = request.form.get("phone")
        genres = request.form.getlist("genres")
        seeking_talent = request.form.get("seeking_talent") == 'y'
        facebook_link = request.form.get("facebook_link")
        website_link = request.form.get("website_link")
        image_link = request.form.get("image_link")
        seeking_description = request.form.get('seeking_description')
        venue = Venue(
            name=name,
            city=city,
            state=state,
            address=address,
            phone=phone,
            facebook_link=facebook_link,
            seeking_talent=seeking_talent,
            image_link=image_link,
            website_link=website_link,
            seeking_description=seeking_description,
        )

        for genre in genres:
            new_genre = Venue_Genre(genre=genre)
            new_genre.venue = venue

        data = venue
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form.get('name') + ' was successfully listed!', 'info')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' + data.name + ' could not be listed.', 'danger')
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('Venue deleted successfully!', 'success')
    except():
        db.session.rollback()
        flash('An error occurred. Please try again', 'danger')
    finally:
        db.session.close()
    return redirect(url_for("index"))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = db.session.query(Artist.id, Artist.name).all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    results = Artist.query.filter(Artist.name.ilike("%" + search_term + "%")).all()
    data = []
    response = {
        "count": len(results),
        "data": data
    }

    for result in results:
        data.append({
            "id": result.id,
            "name": result.name,
            "num_upcoming_shows": count_venue_shows(result.id),
        })

    return render_template('pages/search_artists.html', results=response, search_term=search_term)


def single_artist(artist_id, editing=False):
    artist = Artist.query.filter_by(id=artist_id).outerjoin(Artist_Genre, Artist.id == Artist_Genre.artist_id).first()
    gen = []
    if len(artist.genres) > 0:
        for ge in artist.genres:
            gen.append(ge.genre)

    past_shows = get_artists_shows(artist_id, upcoming=False)
    upcoming_shows = get_artists_shows(artist_id)

    if editing:
        return {
            "id": artist.id,
            "name": artist.name,
            "genres": gen,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website_link,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "image_link": artist.image_link
        }
    return {
        "id": artist.id,
        "name": artist.name,
        "genres": gen,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "image_link": artist.image_link,
        "past_shows": past_shows['data'],
        "upcoming_shows": upcoming_shows['data'],
        "past_shows_count": count_artist_shows(artist_id, False),
        "upcoming_shows_count": count_artist_shows(artist_id),
    }


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    data = single_artist(artist_id)
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = single_artist(artist_id, editing=True)
    form = ArtistForm()
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
        name = request.form.get("name")
        city = request.form.get("city")
        state = request.form.get("state")
        phone = request.form.get("phone")
        genres = request.form.getlist("genres")
        facebook_link = request.form.get("facebook_link")
        image_link = request.form.get("image_link")
        website_link = request.form.get("website_link")
        seeking_venue = request.form.get("seeking_venue") == 'y'
        seeking_description = request.form.get('seeking_description')
        artist = Artist(
            name=name,
            city=city,
            state=state,
            phone=phone,
            facebook_link=facebook_link,
            seeking_venue=seeking_venue,
            image_link=image_link,
            website_link=website_link,
            seeking_description=seeking_description,
        )

        for genre in genres:
            new_genre = Artist_Genre(genre=genre)
            new_genre.artist = artist

        db.session.add(artist)
        db.session.commit()
        flash('Artist information updated successfully!', 'success')
    except:
        db.session.rollback()
        flash('An error occurred. Artist could not be updated.', 'danger')
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = single_venue(venue_id, editing=True)
    form = VenueForm()
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
        name = request.form.get("name")
        city = request.form.get("city")
        state = request.form.get("state")
        address = request.form.get("address")
        phone = request.form.get("phone")
        genres = request.form.getlist("genres")
        seeking_talent = request.form.get("seeking_talent") == 'y'
        facebook_link = request.form.get("facebook_link")
        website_link = request.form.get("website_link")
        image_link = request.form.get("image_link")
        seeking_description = request.form.get('seeking_description')

        venue = Venue.query.get(venue_id)
        venue.name = name
        venue.city = city
        venue.state = state
        venue.address = address
        venue.phone = phone
        venue.facebook_link = facebook_link
        venue.seeking_talent = seeking_talent
        venue.image_link = image_link
        venue.website_link = website_link
        venue.seeking_description = seeking_description

        for genre in genres:
            new_genre = Venue_Genre(genre=genre)
            new_genre.venue = venue

        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form.get('name') + ' was successfully updated!', 'info')
    except:
        db.session.rollback()
        flash('An error occurred. Venue could not be updated.', 'danger')
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    data = {}
    try:
        name = request.form.get("name")
        city = request.form.get("city")
        state = request.form.get("state")
        phone = request.form.get("phone")
        genres = request.form.getlist("genres")
        facebook_link = request.form.get("facebook_link")
        image_link = request.form.get("image_link")
        website_link = request.form.get("website_link")
        seeking_venue = request.form.get("seeking_venue") == 'y'
        seeking_description = request.form.get('seeking_description')
        artist = Artist(
            name=name,
            city=city,
            state=state,
            phone=phone,
            facebook_link=facebook_link,
            seeking_venue=seeking_venue,
            image_link=image_link,
            website_link=website_link,
            seeking_description=seeking_description,
        )

        for genre in genres:
            new_genre = Artist_Genre(genre=genre)
            new_genre.artist = artist

        data = artist
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!', 'success')
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' + data.name + ' could not be listed.', 'danger')
    finally:
        db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    all_shows = db.session.query(Show, Artist, Venue).join(Artist, Venue).all()
    data = []
    for item in all_shows:
        data.append({
            "venue_id": item['Venue'].id,
            "venue_name": item['Venue'].name,
            "artist_id": item['Artist'].id,
            "artist_name": item['Artist'].name,
            "artist_image_link": 'https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80',
            # "artist_image_link": data['Artist'].image_link,
            "start_time": str(item['Show'].start_date_time),
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error_message = ''
    try:
        artist_id = request.form.get("artist_id")
        venue_id = request.form.get("venue_id")
        start_time = request.form.get("start_time")

        check_artist = Artist.query.get(artist_id)
        if check_artist is None:
            error_message = error_message + " Invalid Artist ID"

        check_venue = Venue.query.get(venue_id)
        if check_venue is None:
            error_message = error_message + " Invalid Venue ID"

        show = Show(
            artist_id=artist_id,
            venue_id=venue_id,
            start_date_time=start_time,
        )

        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!', 'success')
    except:
        db.session.rollback()
        flash('An error occurred. Show could not be listed. ' + error_message, 'danger')
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
