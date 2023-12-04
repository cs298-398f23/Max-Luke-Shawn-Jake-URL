from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import redis
import random
import string
import unittest
from urllib.parse import quote, unquote
from flask import abort
from urllib.parse import urlparse
from datetime import datetime, timedelta

def create_app():
    app = Flask(__name__)
    
    redis_client_users = redis.StrictRedis(host='localhost', port=6379, db=0)
    redis_client_urls = redis.StrictRedis(host='localhost', port=6379, db=1)

    app.secret_key = 'your_secret_key'
    login_manager = LoginManager(app)
    login_manager.login_view = 'login'

    class User(UserMixin):
        pass

    @login_manager.user_loader
    def load_user(user_id):
        if user_id == 'admin':
            user = User()
            user.id = 'admin'
            user.email = 'admin@admin.com'
            user.password = 'admin'
            return user

        user_key = f'user:{user_id}'
        stored_password = redis_client_users.hget(user_key, 'password')

        if stored_password:
            user = User()
            user.id = user_id
            user.email = user_id  # Use the user_id as the email for simplicity
            return user

        return None
    
    def is_admin(user):
        return user.id == 'admin'
    
    def format_time(seconds):
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        return f"{days} days, {hours} hours, {minutes} minutes"
    
    def validate_url(original_url, custom_short_url, expiration):
        if not (5 <= len(custom_short_url) < 20):
            return False
        try:
            expiration = int(expiration)
            if expiration not in [1, 60, 1440]:
                return False
        except ValueError:
            return False

        return True


    @app.route('/')
    def initial():
        return render_template('login.html')

    @app.route('/index', methods=['GET', 'POST'])
    def index():
        error = None

        if request.method == 'POST':
            original_url = request.form['original_url']
            custom_short_url = request.form['custom_short_url']
            expiration = request.form['expiration']

            if not validate_url(original_url, custom_short_url, expiration):
                error = 'Invalid URL, Custom Short URL, or Expiration Time. Please enter valid values.'
                return render_template('index.html', error=error)

            if redis_client_urls.exists(custom_short_url):
                error = 'Custom short URL already in use. Please choose another.'
                return render_template('index.html', error=error)

            expiration_time = datetime.utcnow() + timedelta(minutes=int(expiration))

            encoded_url = quote(original_url)
            redis_client_urls.set(custom_short_url, encoded_url, ex=int(expiration) * 60)  # Set expiration time in seconds
            return render_template('shortened.html', short_url=custom_short_url, expiration=expiration_time)

        return render_template('index.html', error=error)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            if email == 'admin@admin.com' and password == 'admin':
                user = load_user('admin')
                login_user(user)

                return redirect(url_for('admin_dashboard'))

            user_key = f'user:{email}'
            stored_password = redis_client_users.hget(user_key, 'password')

            if stored_password and stored_password.decode('utf-8') == password:
                user = load_user(email)
                login_user(user)

                return redirect(url_for('index'))

            else:
                flash('Invalid email or password. Please check your credentials and try again.', 'error')

        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        if is_admin(current_user):
            return render_template('admin_dashboard.html', user=current_user)
        return render_template('dashboard.html', user=current_user)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            user_key = f'user:{email}'
            if redis_client_users.exists(user_key):
                flash('Email already in use. Please choose another email.', 'error')
            else:
                redis_client_users.hset(user_key, 'password', password)
                flash('Account created successfully. You can now log in.', 'success')
                return redirect(url_for('login'))

        return render_template('register.html')

    @app.route('/shorten', methods=['POST'])
    def shorten():
        original_url = request.form['original_url']
        custom_short_url = request.form['custom_short_url']

        if not validate_url(original_url, custom_short_url):
            flash('Invalid URL or custom short URL. Please enter a valid URL and ensure the custom short URL is between 5 and 20 characters.', 'error')
            return redirect(url_for('index'))

        if redis_client_urls.exists(custom_short_url):
            flash('Custom short URL already in use. Please choose another.', 'error')
            return redirect(url_for('index'))

        encoded_url = quote(original_url)
        redis_client_urls.set(custom_short_url, encoded_url)
        return render_template('shortened.html', short_url=custom_short_url)
    
    @app.route('/admin/view_users')
    @login_required
    def view_users():
        if is_admin(current_user):
            user_data = []
            # Retrieve user accounts data from the database
            for key in redis_client_users.scan_iter(match="user:*"):
                email = key.decode("utf-8").split(":")[1]
                password = redis_client_users.hget(key, "password").decode("utf-8")
                user_data.append({"email": email, "password": password})
            return render_template('view_data.html', title="User Accounts", data=user_data)
        else:
            abort(403)  # Forbidden access

    @app.route('/admin/view_urls')
    @login_required
    def view_urls():
        if is_admin(current_user):
            url_data = []
            for key in redis_client_urls.scan_iter():
                short_url = key.decode("utf-8")
                encoded_url = redis_client_urls.get(key).decode("utf-8")

                expiration_time = redis_client_urls.ttl(key)
                expiration_time_str = format_time(expiration_time)
                url_data.append({"short_url": short_url, "original_url": unquote(encoded_url), "expiration_time": expiration_time_str})
            return render_template('view_data.html', title="Shortened URLs", data=url_data)
        else:
            abort(403)
    
    @app.route('/admin')
    @login_required
    def admin_dashboard():
        if is_admin(current_user):
            return render_template('admin_dashboard.html', user=current_user)
        else:
            abort(403) 

    @app.route('/<short_url>')
    def redirect_to_original(short_url):
        encoded_url = redis_client_urls.get(short_url)
        if encoded_url:
            original_url = unquote(encoded_url.decode('utf-8'))

            if not urlparse(original_url).scheme:
                original_url = "http://" + original_url

            return redirect(original_url, code=302)
        else:
            abort(404)

    return app  # Return the Flask application instance

def launch():
    app = create_app()
    return app  # Return the Flask application instance

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
