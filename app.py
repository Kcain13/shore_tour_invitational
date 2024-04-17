from flask import Flask, request, requests, Response, jsonify, json, render_template, flash, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import bcrypt
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import Golfer, db, Club, Round, RoundCourse, RoundStroke, GolferRound, Course, Tee
from forms import RegistrationForm, GolferForm, GolferEditForm, RoundInitiationForm, ScoreCardForm, SearchCourseForm, LoginForm


app = Flask(__name__)


# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///shore_tour_invite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
# Initialize Flask-Migrate with the app and db instance
migrate = Migrate(app, db)
# Initialize the database
db.init_app(app)


@login_manager.user_loader
def load_user(golfer_id):
    return Golfer.query.get(int(golfer_id))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        golfer = Golfer(golfer_name=form.golfer_name.data,
                        username=form.username.data,
                        password=hashed_password,
                        email=form.email.data,
                        GHIN=form.GHIN.data,
                        handicap=form.handicap.data)
        db.session.add(golfer)
        db.session.commit()
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        golfer = Golfer.query.filter_by(username=form.username.data).first()
        if golfer and bcrypt.check_password_hash(golfer.password, form.password.data):
            login_user(golfer)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Define routes for golfer management


@app.route('/golfer/<int:golfer_id>', methods=['GET', 'PUT', 'DELETE'])
def golfer(golfer_id):
    if request.method == 'GET':
        golfer = Golfer.query.get(golfer_id)
        if not golfer:
            return Response(response="Golfer not found", status=404, mimetype="application/text")
        return jsonify(golfer.toJSON()), 200

    if request.method == 'PUT':
        form = GolferEditForm(request.form)
        if form.validate():
            golfer = Golfer.query.get(golfer_id)
            if not golfer:
                return Response(response="Golfer not found", status=404, mimetype="application/text")
            # Update golfer attributes
            golfer.golfer_name = form.golfer_name.data
            golfer.username = form.username.data
            golfer.password = form.password.data
            golfer.email = form.email.data
            golfer.GHIN = form.GHIN.data
            golfer.handicap = form.handicap.data
            golfer.home_course = form.home_course.data
            # Commit changes to the database
            db.session.commit()
            return jsonify(golfer.toJSON()), 200
        else:
            return jsonify(form.errors), 400

    if request.method == 'DELETE':
        golfer = Golfer.query.get(golfer_id)
        if not golfer:
            return Response(response="Golfer not found", status=404, mimetype="application/text")
        # Delete golfer
        db.session.delete(golfer)
        db.session.commit()
        return Response(response="Golfer deleted successfully", status=200, mimetype="application/text")


@app.route('/all_golfers', methods=['GET'])
def all_golfers():
    golfers = Golfer.query.all()
    if not golfers:
        return Response(response="No Golfers found", status=204, mimetype="application/text")
    else:
        return jsonify([golfer.toJSON() for golfer in golfers]), 200


# Define routes for course management

@app.route('/search_course', methods=['GET', 'POST'])
def search_course():
    form = SearchCourseForm()
    if form.validate_on_submit():
        course_name = form.course_name.data
        # Perform search in the database for courses with matching names
        courses = Course.query.filter(
            Course.course_name.ilike(f'%{course_name}%')).all()
        if not courses:  # If no courses found in the database
            # # Make a request to the external API to search for the course name
            # api_url = f"https://example.com/api/search?course_name={course_name}"
            # response = requests.get(api_url)
            # if response.status_code == 200:
            #     data = response.json()
            #     if data:  # If API returns course data
            #         return jsonify(data), 200
            #     else:
            #         return jsonify({'error': 'Course not found'}), 404
            # else:
            #     return jsonify({'error': 'Failed to fetch data from the API'}), 500
        else:
            return render_template('search_results.html', courses=courses)
    return render_template('search_course.html', form=form)


@app.route('/start_round/<int:course_id>', methods=['POST'])
def start_round(course_id):
    match_type = request.form.get('match_type')
    number_of_holes = int(request.form.get('number_of_holes'))
    teebox_id = int(request.form.get('teebox'))

    # Get the course and teebox
    course = Course.query.get(course_id)
    teebox = Tee.query.get(teebox_id)

    # Create a new round
    new_round = Round.begin_round(
        golfer_id=1, club_id=course.club_id, date_of_round=datetime.now())

    # Associate the round with the selected course and teebox
    round_course = RoundCourse(round_id=new_round.round_id,
                               course_id=course_id, tee_id=teebox_id, sequence_number=1)
    db.session.add(round_course)
    db.session.commit()

    # Render the golfer_round.html template and pass necessary data
    return render_template('golfer_round.html', round_id=new_round.round_id, match_type=match_type, number_of_holes=number_of_holes, teebox=teebox, course=course)


@app.route('/record_performance/<round_id>/<int:hole_number>', methods=['POST'])
def record_performance(round_id, hole_number):
    # Retrieve data from the form
    strokes = request.form.get('strokes')
    fairway_hit = request.form.get('fairway_hit')
    green_in_reg = request.form.get('green_in_reg')
    number_of_putts = request.form.get('number_of_putts')
    bunker_shot = request.form.get('bunker_shot')

    # Save the performance data to the database
    round_stroke = RoundStroke(
        golfer_id=current_user.id,  # Assuming current_user is the authenticated golfer
        round_course_id=round_id,
        hole_number=hole_number,
        strokes=strokes,
        fairway_hit=fairway_hit,
        green_in_reg=green_in_reg,
        number_of_putts=number_of_putts,
        bunker_shot=bunker_shot
    )
    db.session.add(round_stroke)
    db.session.commit()

    # Redirect to the view performance page for the next hole
    next_hole_number = hole_number + 1
    return redirect(url_for('view_performance', round_id=round_id, hole_number=next_hole_number))


@app.route('/view_performance/<round_id>/<int:hole_number>')
def view_performance(round_id, hole_number):
    # Retrieve the performance data for the current hole
    round_stroke = RoundStroke.query.filter_by(
        round_course_id=round_id, hole_number=hole_number).first()

    # Check if there's a previous hole
    previous_hole_number = hole_number - 1 if hole_number > 1 else None

    # Check if there's a next hole
    # You need to determine the total number of holes in the round to decide whether there's a next hole
    total_holes = ...  # Get the total number of holes in the round from the database
    next_hole_number = hole_number + 1 if hole_number < total_holes else None

    return render_template('golfer_round.html', round_id=round_id, current_hole_number=hole_number,
                           previous_hole_number=previous_hole_number, next_hole_number=next_hole_number,
                           current_hole_par=round_stroke.par, current_hole_yards=round_stroke.yards)

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


@app.route('/notifications')
def notifications():
    user_id = current_user.id  # Assuming you're using Flask-Login for user authentication
    notifications = Notification.query.filter_by(
        recipient_id=user_id, read=False).all()
    return render_template('notifications.html', notifications=notifications)


@app.route('/mark_notification_as_read/<int:notification_id>', methods=['POST'])
def mark_notification_as_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    notification.read = True
    db.session.commit()
    flash('Notification marked as read.')
    return redirect(url_for('notifications'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8082, debug=True)
