from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'

login_manager = LoginManager()
login_manager.init_app(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy()
db.init_app(app)

# SET UP FLASK LOGIN MANAGER
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

# CREATE TABLE IN DB
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


with app.app_context():
    db.create_all()



@app.route('/')
def home():
    return render_template("index.html", logged_in=current_user.is_authenticated)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        hashedPassword = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=8)
        new_user = User(
            email = request.form.get('email'),
            password = hashedPassword,
            name = request.form.get('name')
        )
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return render_template('secrets.html', name=request.form.get('name'))
    return render_template("register.html", logged_in=current_user.is_authenticated)


@app.route('/login', methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form.get('email')
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if check_password_hash(user.password, request.form.get('password')):
            flash('You were successfully logged in')
            login_user(user)
            return redirect(url_for('secrets'))
        else:
            error = 'Invalid credentials'
    return render_template("login.html", logged_in=current_user.is_authenticated)


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html", name=current_user.name, logged_in=current_user.is_authenticated)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
@login_required
def download():
    return send_from_directory(
        'static', 'files/cheat_sheet.pdf'
    )


if __name__ == "__main__":
    app.run(debug=True, port=9000)
