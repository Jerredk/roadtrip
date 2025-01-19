from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, NumberRange
import os
import openai
import json

client = openai.api_key = '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'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'  # Replace with a real secret key in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///roadtrip_planner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    trips = db.relationship('TripPlan', backref='user', lazy=True)

class TripPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    stops = db.Column(db.Integer, nullable=False)
    time = db.Column(db.Integer, nullable=False)
    preferred_activities = db.Column(db.String(255))
    plan_data = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TripForm(FlaskForm):
    start = StringField('Starting Point', validators=[DataRequired()])
    destination = StringField('Destination', validators=[DataRequired()])
    stops = IntegerField('Number of Stops', validators=[DataRequired(), NumberRange(min=1, max=5)])
    time = IntegerField('Available Time (hours)', validators=[DataRequired(), NumberRange(min=1, max=24)])
    preferred_activities = SelectMultipleField('Preferred Activities', choices=[
        ('sightseeing', 'Sightseeing'),
        ('nature', 'Nature'),
        ('food', 'Food & Dining'),
        ('shopping', 'Shopping'),
        ('culture', 'Culture & History')
    ])
    submit = SubmitField('Plan My Trip')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    trips = TripPlan.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', trips=trips)

@app.route('/plan_trip', methods=['GET', 'POST'])
def plan_trip():
    form = TripForm()
    if form.validate_on_submit():
        trip_plan = plan_trip_with_chatgpt(form.data)
        if current_user.is_authenticated:
            new_trip = TripPlan(
                start=form.start.data,
                destination=form.destination.data,
                stops=form.stops.data,
                time=form.time.data,
                preferred_activities=','.join(form.preferred_activities.data),
                plan_data=str(trip_plan),
                user_id=current_user.id
            )
            db.session.add(new_trip)
            db.session.commit()
            flash('Trip saved successfully!', 'success')
        return render_template('result.html', trip_plan=trip_plan, form_data=form.data)
    return render_template('plan_trip.html', form=form)

def plan_trip_with_chatgpt(form_data):
    # Prepare the prompt in a format compatible with the chat model
    messages = [
        {"role": "system", "content": "You are a helpful assistant that plans road trips."},
        {"role": "user", "content": f"""
        Plan a road trip from {form_data['start']} to {form_data['destination']} with {form_data['stops']} stops.
        The total trip time is {form_data['time']} hours.
        Preferred activities: {', '.join(form_data['preferred_activities'])}.
        For each stop, provide:
        1. Name of the location
        2. Brief description
        3. Estimated time to spend at every stop. Default to 1 hour.
        4. Two short reviews
        """}
    ]

    # Call the ChatCompletion API using the correct endpoint and parameters
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Or "gpt-4" if desired
        messages=messages,
        max_tokens=1000,
        temperature=0.7
    )

    # Access the content correctly from the response
    trip_plan = process_chatgpt_response(response['choices'][0]['message']['content'].strip())
    return trip_plan

def process_chatgpt_response(response):
    lines = response.split('\n')
    stops = []
    current_stop = {}

    for line in lines:
        line = line.strip()
        if line.startswith('Stop'):
            if current_stop:
                stops.append(current_stop)
            current_stop = {'name': line.split(':')[1].strip()}
        elif line.startswith('Description:'):
            current_stop['description'] = line.split(':')[1].strip()
        elif line.startswith('Time to spend:'):
            current_stop['time_to_spend'] = line.split(':')[1].strip()
        elif line.startswith('Review 1:'):
            current_stop['reviews'] = [line.split(':')[1].strip()]
        elif line.startswith('Review 2:'):
            current_stop['reviews'].append(line.split(':')[1].strip())

    if current_stop:
        stops.append(current_stop)

    return {'recommended_stops': stops}

@app.route('/save_trip', methods=['GET', 'POST'])
@login_required
def save_trip():
    form_data = request.form

    # Safely parse trip_plan
    try:
        trip_plan = json.loads(form_data['trip_plan'])  # Assuming it's a JSON string
    except ValueError:
        flash('Invalid trip plan data!', 'error')
        return redirect(url_for('dashboard'))

    # Validate required fields
    start = form_data.get('start')
    destination = form_data.get('destination')
    if not start or not destination:
        flash('Start and destination are required!', 'error')
        return redirect(url_for('dashboard'))

    try:
        new_trip = TripPlan(
            start=start,
            destination=destination,
            stops=int(form_data['stops']),
            time=int(form_data['time']),
            preferred_activities=form_data['preferred_activities'],
            plan_data=str(trip_plan),
            user_id=current_user.id
        )
        db.session.add(new_trip)
        db.session.commit()
        flash('Trip saved successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error saving trip: {str(e)}', 'error')

    return redirect(url_for('dashboard'))

@app.route('/view_trip/<int:trip_id>')
def view_trip(trip_id):
    # Retrieve the trip from the database using the trip_id
    trip = TripPlan.query.get(trip_id)

    # If the trip does not exist, return a 404 error
    if trip is None:
        abort(404, description="Trip not found")

    # Render the template with the trip details
    return render_template('view_trip.html', trip=trip)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

# Used AI to generate the frontend. Made a couple of pages myself such as view_trip.html as well as coded def view_trip and all logic for this
# Learned how to integrate APIs (such as ChatGPT)
# Create database and logic to store data for it
