'''SQLAlchemy models for Shore Tour Invitational'''

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class Golfer(db.Model):
    '''Connection of a Golfer <-> Golfer_Round'''

    __tablename__ = 'golfers'

    golfer_id = db.Column(db.Integer, primary_key=True)
    golfer_name = db.Column(db.Text)
    username = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    GHIN = db.Column(db.Text)
    handicap = db.Column(db.Float)
    home_course = db.Column(db.Text)

    def __repr__(self):
        return f"<User #{self.golfer_id}: {self.username}, {self.email}>"

    @classmethod
    def register(cls, golfer_name, email, username, password, GHIN):

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = Golfer(
            golfer_name,
            email,
            username,
            password,
            GHIN,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

    @classmethod
    # Modify this line to accept 'round_id'
    def generate_golfer_scorecard(self, round_id):
        """Generate the golfer's scorecard for a specific round."""
        # Query all strokes made by the golfer in the given round
        round_strokes = RoundStroke.query.filter_by(
            golfer_id=self.golfer_id, round_course_id=round_id).all()

        scorecard = []
        total_strokes = 0

        # Iterate over each stroke and add it to the scorecard
        for stroke in round_strokes:
            scorecard.append({
                'hole_number': stroke.hole_number,
                'strokes': stroke.strokes,
                'fairway_hit': stroke.fairway_hit,
                'green_in_reg': stroke.green_in_reg,
                'number_of_putts': stroke.number_of_putts,
                'bunker_shot': stroke.bunker_shot
            })
            total_strokes += stroke.strokes

        return scorecard, total_strokes


class Club(db.Model):
    '''Connection of a club <-> course'''
    __tablename__ = 'clubs'

    club_id = db.Column(db.Integer, primary_key=True)
    club_name = db.Column(db.Text)
    city = db.Column(db.Text)
    state = db.Column(db.Text)


class Course(db.Model):
    '''course <-> tee <-> coursehole'''
    __tablename__ = 'courses'

    course_id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.Text)
    club_id = db.Column(db.Integer, db.ForeignKey('club.club_id'))


class CourseHole(db.Model):
    '''many to many relationship with coursehole and tee's'''

    __tablename__ = 'courses_holes'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'))
    number = db.Column(db.Integer)
    par = db.Column(db.Integer)
    handicap = db.Column(db.Integer)


class Tee(db.Model):
    '''one tee can have multiple holes'''
    __tablename__ = 'tees'

    tee_id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'))
    tee_name = db.Column(db.Text)
    slope = db.Column(db.Integer)
    rating = db.Column(db.Float)
    total_yards = db.Column(db.Integer)


class TeeHole(db.Model):
    '''represents holes associated with tees'''
    __tablename__ = 'tee_holes'

    id = db.Column(db.Integer, primary_key=True)
    tee_id = db.Column(db.Integer, db.ForeignKey('tee.tee_id'))
    hole_number = db.Column(db.Integer)
    yards = db.Column(db.Integer)


class GolferRound(db.Model):
    '''represents rounds played by golfers'''
    __tablename__ = 'golfer_rounds'

    golfer_round_id = db.Column(db.Integer, primary_key=True)
    golfer_id = db.Column(db.Integer, db.ForeignKey('golfer.golfer_id'))
    round_id = db.Column(db.Integer)
    total_strokes = db.Column(db.Integer)
    total_holes = db.Column(db.Integer)


class Round(db.Model):
    '''many to many relationship with rounds and courses'''
    __tablename__ = 'rounds'

    round_id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.club_id'))
    date_of_round = db.Column(db.Date)
    golfer_id = db.Column(db.Integer, db.ForeignKey('golfer.golfer_id'))
    golfer = db.relationship('Golfer', backref='rounds')

    @classmethod
    def begin_round(cls, golfer_id, club_id, date_of_round):
        """Create a new round and save it to the database."""
        round = Round(golfer_id=golfer_id, club_id=club_id,
                      date_of_round=date_of_round)
        db.session.add(round)
        db.session.commit()
        return round


class RoundCourse(db.Model):
    '''slecting tee and 9 or 18 holes'''
    __tablename__ = 'rounds_courses'

    round_course_id = db.Column(db.Integer, primary_key=True)
    round_id = db.Column(db.Integer, db.ForeignKey('round.round_id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'))
    sequence_number = db.Column(db.Integer)
    tee_id = db.Column(db.Integer, db.ForeignKey('tee.tee_id'))


class RoundStroke(db.Model):
    '''allows tracking of strokes per hole per round'''
    __tablename__ = 'rounds_strokes'

    id = db.Column(db.Integer, primary_key=True)
    golfer_id = db.Column(db.Integer, db.ForeignKey('golfer.golfer_id'))
    round_course_id = db.Column(
        db.Integer, db.ForeignKey('round_course.round_course_id'))
    hole_number = db.Column(db.Integer)
    strokes = db.Column(db.Integer)
    fairway_hit = db.Column(db.Boolean)
    green_in_reg = db.Column(db.Boolean)
    number_of_putts = db.Column(db.Integer)
    bunker_shot = db.Column(db.Boolean)


class Leaderboard(db.Model):
    '''each leaderboard entry belongs to only one golfer'''
    __tablename__ = 'leaderboards'

    leaderboard_id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(
        db.Integer, db.ForeignKey('tournament.tournament_id'))
    golfer_id = db.Column(db.Integer, db.ForeignKey('golfer.golfer_id'))
    holes_played = db.Column(db.Integer)
    rounds_played = db.Column(db.Integer)
    position = db.Column(db.Integer)


class Tournament(db.Model):
    '''each tournament only has one result'''

    __tablename__ = 'tournaments'

    tournament_id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Text)
    end_date = db.Column(db.Text)
    live_details = db.Column(db.JSON)
    name = db.Column(db.Text)
    type = db.Column(db.Text)
    results_id = db.Column(db.Integer, db.ForeignKey('results.results_id'))
    number_of_players = db.Column(db.Integer)


class Result(db.Model):
    '''can belong to only one tournament'''
    __tablename__ = 'results'

    results_id = db.Column(db.Integer, primary_key=True)
    leaderboard = db.Column(db.JSON)
    tournament = db.Column(db.JSON)


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """
    app.app_context().push()
    db.app = app
    db.init_app(app)
