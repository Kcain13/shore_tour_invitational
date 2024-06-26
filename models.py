'''SQLAlchemy models for Shore Tour Invitational'''

from datetime import datetime

import json

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

    # method to serialize the class instance to a JSON string and all its attributes
    def toJSON(self):
        return json.dumps(self.__dict__, indent=4)


class Club(db.Model):
    '''Connection of a club <-> course'''
    __tablename__ = 'clubs'

    club_id = db.Column(db.Integer, primary_key=True)
    club_name = db.Column(db.Text)
    city = db.Column(db.Text)
    state = db.Column(db.Text)

    def toJSON(self):
        return json.dumps(self.__dict__, indent=4)


class Course(db.Model):
    '''course <-> tee <-> coursehole'''
    __tablename__ = 'courses'

    course_id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.Text)
    club_id = db.Column(db.Integer, db.ForeignKey('club.club_id'))

    def toJSON(self):
        return json.dumps(self.__dict__, indent=4)


class CourseHole(db.Model):
    '''many to many relationship with coursehole and tee's'''

    __tablename__ = 'courses_holes'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'))
    number = db.Column(db.Integer)
    par = db.Column(db.Integer)
    handicap = db.Column(db.Integer)

    def toJSON(self):
        return json.dumps(self.__dict__, indent=4)


class Tee(db.Model):
    '''one tee can have multiple holes'''
    __tablename__ = 'tees'

    tee_id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'))
    tee_name = db.Column(db.Text)
    slope = db.Column(db.Integer)
    rating = db.Column(db.Float)
    total_yards = db.Column(db.Integer)

    def toJSON(self):
        return json.dumps(self.__dict__, indent=4)


class TeeHole(db.Model):
    '''represents holes associated with tees'''
    __tablename__ = 'tee_holes'

    id = db.Column(db.Integer, primary_key=True)
    tee_id = db.Column(db.Integer, db.ForeignKey('tee.tee_id'))
    hole_number = db.Column(db.Integer)
    yards = db.Column(db.Integer)

    def toJSON(self):
        return json.dumps(self.__dict__, indent=4)


class GolferRound(db.Model):
    '''represents rounds played by golfers'''
    __tablename__ = 'golfer_rounds'

    golfer_round_id = db.Column(db.Integer, primary_key=True)
    golfer_id = db.Column(db.Integer, db.ForeignKey('golfer.golfer_id'))
    round_id = db.Column(db.Integer)
    total_strokes = db.Column(db.Integer)
    total_holes = db.Column(db.Integer)

    def toJSON(self):
        return json.dumps(self.__dict__, indent=4)


class Round(db.Model):
    '''many to many relationship with rounds and courses'''
    __tablename__ = 'rounds'

    round_id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.club_id'))
    date_of_round = db.Column(db.Date)
    golfer_id = db.Column(db.Integer, db.ForeignKey('golfer.golfer_id'))
    golfer = db.relationship('Golfer', backref='rounds')

    def toJSON(self):
        return json.dumps(self.__dict__, indent=4)

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

    def toJSON(self):
        return json.dumps(self.__dict__, indent=4)


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

    def toJSON(self):
        return json.dumps(self.__dict__, indent=4)


class Leaderboard(db.Model):
    '''Model to store leaderboard data'''
    __tablename__ = 'leaderboards'

    leaderboard_id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(
        db.Integer, db.ForeignKey('tournament.tournament_id'))
    golfer_id = db.Column(db.Integer, db.ForeignKey('golfer.golfer_id'))
    round_id = db.Column(db.Integer, db.ForeignKey('round.round_id'))
    play_type = db.Column(db.String(50))
    score = db.Column(db.Integer)
    position = db.Column(db.Integer)

    def calculate_score(self, play_type):
        # Calculate score based on play type
        # You can customize this method to calculate scores differently based on play type
        if play_type == 'match':
            # Example calculation logic for match play
            return self.holes_played - self.score  # Assuming score represents holes won
        elif play_type == 'stroke':
            # Example calculation logic for stroke play
            return self.score
        elif play_type == 'tournament':
            # Example calculation logic for tournament play
            return self.score

    @classmethod
    def update_leaderboard(cls, round_id, play_type):
        # Fetch all golfer rounds for the given round and play type
        golfer_rounds = GolferRound.query.filter_by(
            round_id=round_id, play_type=play_type).all()

        # Dictionary to store scores for each golfer
        scores = {}

        for golfer_round in golfer_rounds:
            golfer_id = golfer_round.golfer_id
            if golfer_id not in scores:
                scores[golfer_id] = 0

            # Calculate score for each golfer round
            scores[golfer_id] += golfer_round.calculate_score(play_type)

        # Sort scores and update leaderboard positions
        sorted_scores = sorted(
            scores.items(), key=lambda x: x[1], reverse=True)
        position = 1
        for golfer_id, score in sorted_scores:
            leaderboard_entry = cls.query.filter_by(
                round_id=round_id, golfer_id=golfer_id, play_type=play_type).first()
            if leaderboard_entry:
                leaderboard_entry.score = score
                leaderboard_entry.position = position
            else:
                leaderboard_entry = cls(
                    round_id=round_id, golfer_id=golfer_id, play_type=play_type, score=score, position=position)
                db.session.add(leaderboard_entry)
            position += 1

        db.session.commit()


class Tournament(db.Model):
    '''each tournament only has one result'''

    __tablename__ = 'tournaments'

    tournament_id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.Text)
    course = db.Column(db.Text)
    course_par = db.Column(db.Text)
    end_date = db.Column(db.Text)
    live_details = db.Column(db.JSON)
    name = db.Column(db.Text)
    start_date = db.Column(db.Text)
    timezone = db.Column(db.Text)
    tour_id = db.Column(db.Text)
    type = db.Column(db.Text)
    results_id = db.Column(db.Integer, db.ForeignKey('results.results_id'))

    def toJSON(self):
        return json.dumps(self.__dict__, indent=4)


class Result(db.Model):
    '''can belong to only one tournament'''
    __tablename__ = 'results'

    results_id = db.Column(db.Integer, primary_key=True)
    leaderboard = db.Column(db.JSON)
    tournament = db.Column(db.JSON)

    def toJSON(self):
        return json.dumps(self.__dict__, indent=4)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'))
    message = db.Column(db.String(255))
    read = db.Column(db.Boolean, default=False)

    def send_invitation_notification(sender, recipient, match):
    message = f"You've been invited to join a {match.match_type} match by {sender.username}."
    notification = Notification(
        recipient_id=recipient.id, sender_id=sender.id, match_id=match.id, message=message)
    db.session.add(notification)
    db.session.commit()

    # Define routes for match play results, stroke play results, and tournament play results


@app.route('/match_results')
def match_results():
    # Retrieve leaderboard data for match play from the database
    leaderboard_entries = retrieve_match_leaderboard_data()
    # Render the match results template with the leaderboard data
    return render_template('match_results.html', leaderboard_entries=leaderboard_entries)


@app.route('/stroke_results')
def stroke_results():
    # Retrieve leaderboard data for stroke play from the database
    leaderboard_entries = retrieve_stroke_leaderboard_data()
    # Render the stroke results template with the leaderboard data
    return render_template('stroke_results.html', leaderboard_entries=leaderboard_entries)


@app.route('/tournament_results')
def tournament_results():
    # Retrieve leaderboard data for tournament play from the database
    leaderboard_entries = retrieve_tournament_leaderboard_data()
    # Render the tournament results template with the leaderboard data
    return render_template('tournament_results.html', leaderboard_entries=leaderboard_entries)


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """
    app.app_context().push()
    db.app = app
    db.init_app(app)
