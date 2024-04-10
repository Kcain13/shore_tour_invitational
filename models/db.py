from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Golfer(db.Model):
    golfer_id = db.Column(db.Integer, primary_key=True)
    golfer_name = db.Column(db.Text)
    username = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    GHIN = db.Column(db.Text)
    handicap = db.Column(db.Float)


class Club(db.Model):
    club_id = db.Column(db.Integer, primary_key=True)
    club_name = db.Column(db.Text)
    city = db.Column(db.Text)
    state = db.Column(db.Text)


class Course(db.Model):
    course_id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.Text)
    club_id = db.Column(db.Integer, db.ForeignKey('club.club_id'))


class CourseHole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'))
    number = db.Column(db.Integer)
    par = db.Column(db.Integer)
    handicap = db.Column(db.Integer)


class Tee(db.Model):
    tee_id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'))
    tee_name = db.Column(db.Text)
    slope = db.Column(db.Integer)
    rating = db.Column(db.Float)
    total_yards = db.Column(db.Integer)


class TeeHole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tee_id = db.Column(db.Integer, db.ForeignKey('tee.tee_id'))
    hole_number = db.Column(db.Integer)
    yards = db.Column(db.Integer)


class GolferRound(db.Model):
    golfer_round_id = db.Column(db.Integer, primary_key=True)
    golfer_id = db.Column(db.Integer, db.ForeignKey('golfer.golfer_id'))
    round_id = db.Column(db.Integer)
    total_strokes = db.Column(db.Integer)
    total_holes = db.Column(db.Integer)


class Round(db.Model):
    round_id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.club_id'))
    date_of_round = db.Column(db.Date)


class RoundCourse(db.Model):
    round_course_id = db.Column(db.Integer, primary_key=True)
    round_id = db.Column(db.Integer, db.ForeignKey('round.round_id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'))
    sequence_number = db.Column(db.Integer)
    tee_id = db.Column(db.Integer, db.ForeignKey('tee.tee_id'))


class RoundStroke(db.Model):
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
    leaderboard_id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(
        db.Integer, db.ForeignKey('tournament.tournament_id'))
    golfer_id = db.Column(db.Integer, db.ForeignKey('golfer.golfer_id'))
    holes_played = db.Column(db.Integer)
    position = db.Column(db.Integer)


class Tournament(db.Model):
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


class Result(db.Model):
    results_id = db.Column(db.Integer, primary_key=True)
    leaderboard = db.Column(db.JSON)
    tournament = db.Column(db.JSON)
