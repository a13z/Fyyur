from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL, ValidationError, Regexp, Length, Optional
from enums import Genre, State

def anyof_for_multiple_field(values):
    message = 'Invalid value, must be one of: {0}.'.format( ','.join(values) )
    def _validate(form, field):
        error = False
        for value in field.data:
            if value not in values:
                error = True
        if error:
            raise ValidationError(message)
    return _validate

class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired(), AnyOf([choice.value for choice in State ])],
        choices=State.choices()
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        # DONE implement validation logic for state
        'phone',
        validators=[Regexp('^[0-9]{3}-[0-9]{3}-[0-9]{5}$'), Optional()]
    )
    genres = SelectMultipleField(
        # DONE implement enum restriction
        'genres', 
        validators=[DataRequired(), anyof_for_multiple_field([choice.value for choice in Genre])],
        choices=Genre.choices()
    )
    facebook_link = StringField(
        'facebook_link', 
        validators=[URL(), Length(-1,120), Optional()]
    )
    image_link = StringField(
        'image_link', 
        validators=[URL(), Length(-1,500), Optional()]
    )
    website = StringField(
        'website', 
        validators=[URL(), Length(-1,120), Optional()]
    )    
    seeking_talent = BooleanField(
        'seeking_talent'
    )
    seeking_description = StringField(
        'seeking_description',
        validators=[Optional()]
    )

class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired(), Length(-1,120)]
    )
    city = StringField(
        'city', validators=[DataRequired(), Length(-1,120)]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=State.choices()
    )
    phone = StringField(
        # DONE implement validation logic for state
        'phone',
        validators=[Regexp('^[0-9]{3}-[0-9]{3}-[0-9]{5}$'), Optional()]
    )
    genres = SelectMultipleField(
        # DONE implement enum restriction
        'genres', 
        validators=[DataRequired(), anyof_for_multiple_field([choice.value for choice in Genre])],
        choices=Genre.choices()
    )
    facebook_link = StringField(
        'facebook_link', 
        validators=[URL(), Length(-1,120), Optional()]
    )
    image_link = StringField(
        'image_link', 
        validators=[URL(), Length(-1,500), Optional()]
    )
    website = StringField(
        'website', 
        validators=[URL(), Length(-1,120), Optional()]
    )    
    seeking_venue = BooleanField(
        'seeking_venue'
    )
    seeking_description = StringField(
        'seeking_description',
        validators=[Optional()]
    )