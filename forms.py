from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField, SearchField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError
from models import Tournament, Tee, Course


class RegistrationForm(FlaskForm):
    '''Form for registering golfers'''
    golfer_name = StringField('Full Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    passwword = PasswordField('Password', validators=[Length(min=8)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    GHIN = IntegerField('GHIN ID', validators=[Optional()])
    handicap = IntegerField('Current Handicap', validators=[DataRequired()])


class LoginForm(FlaskForm):
    '''login form'''
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=8)])


class GolferEditForm(FlaskForm):
    golfer_name = StringField('Full Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=8)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    GHIN = IntegerField('GHIN ID', validators=[Optional()])
    handicap = IntegerField('Current Handicap', validators=[DataRequired()])
    home_course = StringField('home_course', validators=[DataRequired()])


class SearchCourseForm(FlaskForm):
    course_name = SearchField('Enter Course Name',
                              validators=[DataRequired()])
    submit = SubmitField('Search')


class RoundInitiationForm(FlaskForm):
    '''Form for initiating a round'''

    course_name = StringField('Course Name', validators=[DataRequired()])

    play_options = SelectField('Play Options', choices=[
        ('match', 'Match Play'), ('stroke', 'Stroke Play'), ('tournament', 'Tournament Play')], validators=[DataRequired()])

    enable_handicap = BooleanField('Enable Handicap')

    submit = SubmitField('Start Round')

    def validate_course_name(self, field):
        course = Course.query.filter_by(course_name=field.data).first()
        if not course:
            raise ValidationError('Invalid course name.')

    def __init__(self, *args, **kwargs):
        super(RoundInitiationForm, self).__init__(*args, **kwargs)
        if 'course_name' in kwargs:
            course_name = kwargs['course_name']
            course = Course.query.filter_by(course_name=course_name).first()
            if course:
                self.course_id = course.id
                teeboxes = Tee.query.filter_by(course_id=course.id).all()
                self.teebox_choices = [(str(tee.id), tee.tee_name)
                                       for tee in teeboxes]
                self.teebox.choices = self.teebox_choices


class ScoreCardForm(FlaskForm):
    strokes = IntegerField('Strokes', validators=[DataRequired()])
    fairway_hit = BooleanField('Fairway Hit')
    green_in_reg = BooleanField('Green in Regulation')
    number_of_putts = IntegerField(
        'Number of Putts', validators=[DataRequired()])
    bunker_shot = BooleanField('Bunker Shot')


# class TournamentRegistrationForm(FlaskForm):
#     # Fetch all tournaments from the database
#     tournaments = Tournament.query.all()

#     # Create choices for the select field using tournament names
#     tournament_choices = [(str(tournament.id), tournament.name)
#                           for tournament in tournaments]

#     # Add a select field with tournament choices
#     tournament = SelectField(
#         'Tournament', choices=tournament_choices, validators=[DataRequired()])


class TeeboxSelectionForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(TeeboxSelectionForm, self).__init__(*args, **kwargs)
        # Get the course_id passed to the form
        self.course_id = kwargs.get('course_id')

        # Fetch all teeboxes for the selected course
        self.teeboxes = Tee.query.filter_by(course_id=self.course_id).all()

        # Create choices for the select field using teebox names
        teebox_choices = [(str(tee.id), tee.tee_name) for tee in self.teeboxes]

        # Add a select field with teebox choices
        self.teebox = SelectField(
            'Teebox', choices=teebox_choices, validators=[DataRequired()])
