import json
import click

from datetime import datetime
from dateutil.parser import parse
from app import db, Artist, Venue, Show

from flask import Flask 
from flask.cli import AppGroup

app = Flask(__name__)

@app.cli.command("seed_db")
def seed_db():
    with open('db/fixtures/artists_seed.json') as json_file:
        seed_data = json.load(json_file)
        for element in seed_data:
            new_object = Artist()
            new_object.id = element.get('id')
            new_object.name = element.get('name', '')
            new_object.genres = ','.join(element.get('genres', ''))
            new_object.city = element.get('city', '')
            new_object.state = element.get('state', '')
            new_object.phone = element.get('phone', '')
            new_object.website = element.get('website', '')
            new_object.facebook_link = element.get('facebook_link', '')
            new_object.seeking_venue = element.get('seeking_venue', '')
            new_object.seeking_description  = element.get('seeking_description', '')
            new_object.image_link = element.get('image_link', '')

            db.session.add(new_object)
            db.session.commit()

    with open('db/fixtures/venues_seed.json') as json_file:
        seed_data = json.load(json_file)
        for element in seed_data:
            new_object = Venue()
            new_object.id = element.get('id')
            new_object.name = element.get('name', '')
            new_object.genres = ','.join(element.get('genres', ''))
            new_object.address = element.get('address', '')
            new_object.city = element.get('city', '')
            new_object.state = element.get('state', '')
            new_object.phone = element.get('phone', '')
            new_object.website = element.get('website', '')
            new_object.facebook_link = element.get('facebook_link', '')
            new_object.seeking_talent = element.get('seeking_talent', '')
            new_object.seeking_description  = element.get('seeking_description', '')
            new_object.image_link = element.get('image_link', '')

            db.session.add(new_object)
            db.session.commit()


    with open('db/fixtures/shows_seed.json') as json_file:
        seed_data = json.load(json_file)
        for element in seed_data:
            new_object = Show()
            new_object.artist_id = element.get('artist_id')
            new_object.venue_id = element.get('venue_id')
            new_object.start_time = parse(element.get('start_time'))

            db.session.add(new_object)
            db.session.commit()


# app.cli.add_command(user_cli)
if __name__ == '__main__':
    seed_db()