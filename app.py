from flask import Flask, render_template, request, redirect, url_for, abort
import redis
import random
import string
from urllib.parse import quote
import urllib.request
import urllib.error

def create_app():
    app = Flask(__name__)
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    def generate_short_url():
        characters = string.ascii_letters + string.digits
        short_url = ''.join(random.choice(characters) for i in range(5))
        return short_url

    def shorten_with_tinyurl(long_url):
        try:
            url = f'http://tinyurl.com/api-create.php?url={quote(long_url)}'
            with urllib.request.urlopen(url) as response:
                if response.getcode() == 200:
                    return response.read().decode("utf-8")
                else:
                    return None
        except urllib.error.URLError as e:
            print(f"Error shortening URL with TinyURL: {e}")
            return None

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/shorten', methods=['POST'])
    def shorten():
        original_url = request.form['original_url']
        
        # Use TinyURL to shorten the URL
        tinyurl = shorten_with_tinyurl(original_url)

        if tinyurl:
            redis_client.set(tinyurl, original_url)
            return render_template('shortened.html', short_url=tinyurl)
        else:
            return "Error shortening URL", 500

    @app.route('/<short_url>')
    def redirect_to_original(short_url):
        original_url = redis_client.get(short_url)

        if original_url:
            return redirect(original_url.decode('utf-8'), code=302)
        else:
            abort(404)

    return app

def launch():
    return create_app()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)

