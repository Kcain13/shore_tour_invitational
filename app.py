from forms import RegistrationForm, LoginForm  # Assuming you have forms defined
from models import Golfer  # Assuming you have a Golfer model defined
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate  # Import Flask-Migrate
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
# Initialize Flask-Migrate with the app and db instance
migrate = Migrate(app, db)

# Import models and forms


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


if __name__ == '__main__':
    app.run(debug=True)
