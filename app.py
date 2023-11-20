from flask import Flask, render_template, request, redirect, url_for
import redis
import random
import string
from urllib.parse import quote, unquote
from flask import abort
from urllib.parse import urlparse

def create_app():

    app = Flask(__name__)
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    def generate_short_url():
        characters = string.ascii_letters + string.digits
        short_url = ''.join(random.choice(characters) for i in range(5))
        return short_url

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/shorten', methods=['POST'])
    def shorten():
        original_url = request.form['original_url']
        short_url = generate_short_url()
        encoded_url = quote(original_url)  
        print(f"Encoded URL: {encoded_url}")  
        redis_client.set(short_url, encoded_url)
        return render_template('shortened.html', short_url=short_url)


    @app.route('/<short_url>')
    def redirect_to_original(short_url):
        encoded_url = redis_client.get(short_url)
        if encoded_url:
            original_url = unquote(encoded_url.decode('utf-8')) 

            if not urlparse(original_url).scheme:
                original_url = "http://" + original_url 

            return redirect(original_url, code=302)
        else:
            abort(404)
    return app

def launch():
    return create_app()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=8000)
