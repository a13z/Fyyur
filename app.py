#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from marshmallow import (
    Schema,
    fields,
    validate,
    ValidationError,
)
from flask_wtf.csrf import CsrfProtect

from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)

csrf = CsrfProtect()
csrf.init_app(app)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(120))

    def __repr__(self):
      return f'<Artist: {self.name}>'
    
    def upcoming_shows(self):
      shows = Show.query.filter(Show.artist_id==self.id, Show.start_time >= datetime.now()).order_by('start_time')
      return shows

    def past_shows(self):
      shows = Show.query.filter(Show.artist_id==self.id, Show.start_time < datetime.now()).order_by(db.desc('start_time'))
      return shows

class Show(db.Model):
    __tablename__ = 'Show'
    
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    start_time = db.Column(db.DateTime())
    artist = db.relationship("Artist", backref="shows")
    venue = db.relationship("Venue", backref="shows")

    def __repr__(self):
      return f'<Show date: {self.start_time}, {self.artist.name} playing at {self.venue.name}>'
    
    def upcoming_shows(self):
      shows = Show.query.filter(Show.start_time >= datetime.now()).order_by('start_time')
      return shows

    def past_shows(self):
      shows = Show.query.filter(Show.start_time < datetime.now()).order_by(db.desc('start_time'))
      return shows

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(120))
    artists = db.relationship("Artist", secondary=Show.__table__, backref='venues')
    
    def __repr__(self):
        return f'<Venue :{self.name}>'

    def upcoming_shows(self):
      shows = Show.query.filter(Show.venue_id==self.id, Show.start_time >= datetime.now()).order_by('start_time')
      return shows

    def past_shows(self):
      shows = Show.query.filter(Show.venue_id==self.id, Show.start_time < datetime.now()).order_by(db.desc('start_time'))
      return shows
      
#----------------------------------------------------------------------------#
# Schemas.
#----------------------------------------------------------------------------#
class VenueSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Venue

    id = ma.auto_field()
    name = ma.auto_field()
    city = ma.auto_field()
    state = ma.auto_field()
    phone = ma.auto_field()
    image_link = ma.auto_field()
    facebook_link = ma.auto_field()
    genres = fields.Method("get_genres")
    website = ma.auto_field()
    seeking_talent = ma.auto_field()
    seeking_description = ma.auto_field()
    num_upcoming_shows = fields.Method("get_num_upcoming_shows")

    def get_num_upcoming_shows(self, venue):
        shows = Show.query.filter(Show.venue_id==venue.id, Show.start_time >= datetime.now()).count()
        return shows

    def get_genres(self, obj):
        return obj.genres.split(',')

class VenueByCityStateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Venue
        fields = ('city', 'state')

class ShowSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Show
    
    venue_id = ma.auto_field()
    venue_name = fields.Method("get_venue_name")
    artist_id = ma.auto_field()
    artist_name = fields.Method("get_artist_name")
    artist_image_link = fields.Method("get_artist_image_link")
    start_time = ma.auto_field()

    def get_artist_name(self, obj):
        return  obj.artist.name

    def get_artist_image_link(self, obj):
        return  obj.artist.image_link

    def get_venue_name(self, obj):
        return  obj.venue.name

class ArtistShowSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Show
        # include_relationships = True
        field = ('start_time',)

class ArtistSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Artist

    id = ma.auto_field()
    name = ma.auto_field()
    city = ma.auto_field()
    state = ma.auto_field()
    phone = ma.auto_field()
    image_link = ma.auto_field()
    facebook_link = ma.auto_field()
    genres = fields.Method("get_genres")
    website = ma.auto_field()
    seeking_venue = ma.auto_field()
    seeking_description = ma.auto_field()
    shows = ma.Nested(ArtistShowSchema, many=True)
    num_upcoming_shows = fields.Method("get_num_upcoming_shows")

    def get_num_upcoming_shows(self, artist):
        shows = Show.query.filter(Show.artist_id==artist.id, Show.start_time >= datetime.now()).count()
        return shows

    def get_genres(self, obj):
        return obj.genres.split(',')

artist_schema = ArtistSchema()
venue_schema = VenueSchema()
show_schema = ShowSchema()

artists_schema = ArtistSchema(many=True)
venues_schema = VenueSchema(many=True)
venues_by_city_state_schema = VenueByCityStateSchema()
shows_schema = ShowSchema(many=True)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # DONE: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    data = []
    city_area = {}
    areas = Venue.query.with_entities(Venue.city, Venue.state).distinct('city','state').all()
    for area in areas:
        city_area = venues_by_city_state_schema.dump(area)
        venues = Venue.query.filter(Venue.city == area.city, Venue.state == area.state).all()
        city_area['venues'] = venues_schema.dump(venues)
        data.append(city_area)

    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    response = {}
    term = request.form.get('search_term', '')
    response['data'] = Venue.query.filter(Venue.name.ilike(f'%{term}%')).all()
    response['count'] = len(response['data'])

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # DONE: replace with real venue data from the venues table, using venue_id

    venue = Venue.query.get_or_404(venue_id)
    # Get the venue data from MA VenueSchema
    data = venue_schema.dump(venue)
    past_shows = []
    upcoming_shows = []
    for show in venue.past_shows():
        show_json = {}
        show_json['artist_id'] = show.artist_id
        show_json['artist_name'] = show.artist.name
        show_json['artist_image_link'] = show.artist.image_link
        show_json['start_time'] = show.start_time.isoformat()
        past_shows.append(show_json)

    data['past_shows'] = past_shows

    for show in venue.upcoming_shows():
        show_json = {}
        show_json['artist_id'] = show.artist_id
        show_json['artist_name'] = show.artist.name
        show_json['artist_image_link'] = show.artist.image_link
        show_json['start_time'] = show.start_time.isoformat()
        upcoming_shows.append(show_json)

    data['upcoming_shows'] = upcoming_shows

    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()  
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
    form = VenueForm()
    list_genres = request.form.getlist('genres')
    try:
        new_venue = Venue(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            address=request.form['address'],
            phone=request.form['phone'],
            # Genres are fetch as a list and then converted to string to store in db
            genres = ','.join(list_genres),
            image_link=request.form['image_link'],
            facebook_link=request.form['facebook_link'],
            website=request.form['website'],
            seeking_talent=True if request.form.get('seeking_talent') == 'y' else False,
            seeking_description=request.form['seeking_description']
        )

        db.session.add(new_venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')   
                
    except Exception as e:
        db.session.rollback()
        error = True
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        print(sys.exc_info())
        print(e)
    finally:
        db.session.close()
  
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # DONE: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        error = True
        print(sys.exc_info())
        print(e)
        return jsonify({ 'success': False })
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return jsonify({ 'success': True })

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # DONE: replace with real data returned from querying the database
    data = Artist.query.with_entities(Artist.id, Artist.name).all()
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    response = {}
    term = request.form.get('search_term', '')
    response['data'] = artists_schema.dump(Artist.query.filter(Artist.name.ilike(f'%{term}%')).all())
    response['count'] = len(response['data'])

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # DONE: replace with real venue data from the venues table, using venue_id

    artist = Artist.query.get_or_404(artist_id)
    data = artist_schema.dump(artist)
    past_shows = []
    upcoming_shows = []
    for show in artist.past_shows():
        show_json = {}
        show_json['venue_id'] = show.venue_id
        show_json['venue_name'] = show.venue.name
        show_json['venue_image_link'] = show.venue.image_link
        show_json['start_time'] = show.start_time.isoformat()
        past_shows.append(show_json)

    data['past_shows'] = past_shows

    for show in artist.upcoming_shows():
        show_json = {}
        show_json['venue_id'] = show.venue_id
        show_json['venue_name'] = show.venue.name
        show_json['venue_image_link'] = show.venue.image_link
        show_json['start_time'] = show.start_time.isoformat()
        upcoming_shows.append(show_json)

    data['upcoming_shows'] = upcoming_shows

    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # DONE: populate form with fields from artist with ID <artist_id>
    artist = Artist.query.get_or_404(artist_id)
    form = ArtistForm(obj=artist)
   
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # DONE: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    
    artist = Artist.query.get_or_404(artist_id)
    form = ArtistForm(obj=artist)

    if form.validate():
        try:
          artist.name=request.form['name']
          artist.city=request.form['city']
          artist.state=request.form['state']
          artist.phone=request.form['phone']
          # Genres are fetch as a list and then converted to string to store in db
          list_genres = request.form.getlist('genres')
          artist.genres = ','.join(list_genres)
          artist.image_link=request.form['image_link']
          artist.facebook_link=request.form['facebook_link']
          artist.website=request.form['website']
          artist.seeking_venue=True if request.form.get('seeking_venue') == 'y' else False
          artist.seeking_description=request.form['seeking_description']

          db.session.add(artist)
          db.session.commit()
          flash('Artist ' + request.form['name'] + ' was successfully updated!')
        except Exception as e:
            db.session.rollback()
            error = True
            print(sys.exc_info())
            flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
            print(sys.exc_info())
            print(e)
        finally:
            db.session.close()
    else:
        flash(form.errors)
        return redirect(url_for('edit_artist', artist_id=artist_id))

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # DONE: populate form with values from venue with ID <venue_id>
    venue = Venue.query.get_or_404(venue_id)
    form = VenueForm(obj=venue)
  
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # DONE: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.get_or_404(venue_id)
    form = VenueForm()
    print("Form validate", form.validate())
    print(form.errors)
    if form.validate_on_submit():
        try:
          print(request.form)
          venue.name=request.form['name']
          venue.address=request.form['address']
          venue.city=request.form['city']
          venue.state=request.form['state']
          venue.phone=request.form['phone']
          # Genres are fetch as a list and then converted to string to store in db
          list_genres = request.form.getlist('genres')
          venue.genres = ','.join(list_genres)
          venue.image_link=request.form['image_link']
          venue.facebook_link=request.form['facebook_link']
          venue.website=request.form['website']
          venue.seeking_talent=True if request.form.get('seeking_talent') == 'y' else False
          venue.seeking_description=request.form['seeking_description']

          db.session.add(venue)
          db.session.commit()
          flash('Venue ' + request.form['name'] + ' was successfully updated!')
        except Exception as e:
            db.session.rollback()
            error = True
            print(sys.exc_info())
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
            print(sys.exc_info())
            print(e)
        finally:
            db.session.close()
    else:
        flash(form.errors)
        return redirect(url_for('edit_venue', venue_id=venue_id))
    
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # DONE: insert form data as a new Venue record in the db, instead
    # DONE: modify data to be the data object returned from db insertion

    form = ArtistForm()
    list_genres = request.form.getlist('genres')
    if form.validate():
        try:
            new_artist = Artist(
                name=request.form['name'],
                city=request.form['city'],
                state=request.form['state'],
                phone=request.form['phone'],
                # Genres are fetch as a list and then converted to string to store in db
                genres = ','.join(list_genres),
                image_link=request.form['image_link'],
                facebook_link=request.form['facebook_link'],
                website=request.form['website'],
                seeking_venue=True if request.form.get('seeking_venue') == 'y' else False,
                seeking_description=request.form['seeking_description']
            )

            db.session.add(new_artist)
            db.session.commit()
            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] + ' was successfully listed!')

        except Exception as e:
            db.session.rollback()
            error = True
            print(sys.exc_info())
            flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
            print(sys.exc_info())
            print(e)
        finally:
            db.session.close()
    else:
        flash(form.errors)
        return redirect(url_for('create_artist_submission'))

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # DONE: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    data = shows_schema.dump(Show.query.filter(Show.start_time >= datetime.now()).order_by('start_time'))

    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # DONE: insert form data as a new Show record in the db, instead

    try:
        new_show = Show(
            artist_id=request.form['artist_id'],
            venue_id=request.form['venue_id'],
            start_time=request.form['start_time'],
        )

        db.session.add(new_show)
        db.session.commit()
        flash('Show was successfully listed!')

    except Exception as e:
        db.session.rollback()
        error = True
        print(sys.exc_info())
        flash('An error occurred. Show could not be listed.')
        print(sys.exc_info())
        print(e)
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

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
