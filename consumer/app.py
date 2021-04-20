import requests
from flask import Flask, redirect, render_template, session
from flask.globals import request
from flask.helpers import url_for
from flask_cors import CORS

import settings
from models import User, db

CONFIG = {
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///consumer_db.sqlite',
    'SECRET_KEY': b'_5#y2L"F4Q8z\n\xec]/',
}

app = Flask(__name__)
app.config.from_object(settings)
CORS(app)

db.init_app(app)

PROVIDER_BASE_URL = "http://127.0.0.1:5000/oauth"
PROVIDER_PROTECTED_BASE_URL = "http://localhost:5000/provider/oauth2/protected"
CLIENT_ID = "5udiNw8knA8WoTLlhVNfJeNV"
CLIENT_SECRET = "Qn2X4znEUOd4LoyH0Jq7BnE25UWoDOBle1dkmHXc4CebMoQz"
BASE64_SECRET = "NXVkaU53OGtuQThXb1RMbGhWTmZKZU5WOlFuMlg0em5FVU9kNExveUgwSnE3Qm5FMjVVV29ET0JsZTFka21IWGM0Q2ViTW9Reg=="


def current_user() -> User:
    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)
    return None

def associate_user_with_token(token):
    user = current_user()
    if not user:
        raise ValueError('Not an authorized user')
    user.oauth2_token = token
    db.session.add(user)
    db.session.commit()


@app.route('/')
def index():
    user = current_user()
    if user:
        oauth_info = None
        if user.oauth2_token:
            url = 'http://127.0.0.1:5000/api/me'
            headers = {
            'Authorization': f'Bearer {user.oauth2_token}'
            }
            response = requests.request('GET', url, headers=headers,)
            oauth_info = response.json()
        return render_template('home.html', user=user, linked_user=oauth_info)
    else:
        return redirect(url_for('login_webpage', next="/"))

@app.route('/consumer/login', methods=['GET', 'POST'])
def login_webpage():
    """
    This handles logging-in into the consumer site
    """
    if request.method == 'POST':
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()
        session['id'] = user.id
        # if user is not just to log in, but need to head back to the auth page, then go for it
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect('/')

    return render_template('login.html')

@app.route('/consumer/oauth2/vulnerable/login', methods=['GET'])
def vulnerable_login():
    # This is implemented without the state parameter
    provider_url = f"{PROVIDER_BASE_URL}/authorize"
    redirect_uri = "?redirect_uri=http://localhost:4000/consumer/oauth2/vulnerable/callback"
    client_id = "&client_id=" + "consumer"
    return redirect(provider_url + "?" + redirect_uri + client_id)

@app.route("/consumer/oauth2/vulnerable/callback", methods=['GET'])
def vulnerable_callback():
    code = request.args.get('code')
    if not code:
        return {"message": "Invalid code"}, 400
    
    url = f'{PROVIDER_BASE_URL}/token?grant_type=authorization_code'
    headers = {
        'Authorization': f'Basic {BASE64_SECRET}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = [('code', code)]
    response = requests.request('POST', url, data=data, headers=headers,)
    response_json = response.json()
    token = response_json['access_token']
    associate_user_with_token(token)
    return response_json


@app.route('/consumer/oauth2/protected/login', methods=['GET'])
def protected_login():
    # TODO: Correctly implement this
    provider_url = "http://localhost:5000/provider/oauth2/protected/login"
    redirect_uri = "redirect_uri=http://localhost:4000/consumer/oauth2/protected/callback"
    client_id = "&client_id=" + "consumer"
    state = "&state=abcd"
    session['state'] = 'abcd'
    return redirect(provider_url + "?" + redirect_uri + client_id + state)

@app.route("/consumer/oauth2/protected/callback", methods=['GET'])
def protected_callback():
    # TODO: Correctly implement this
    code = request.args.get('code')
    state = request.args.get('state')
    stored_state = session['state']
    print(stored_state, state)
    if not state == stored_state:
        return {"message": "Invalid request - possible CSRF"}
    if not code:
        return {"message": "Invalid code"}, 400
    get_access_token = requests.post(f'{PROVIDER_BASE_URL}/token', )
    print(get_access_token.text)
    return get_access_token.json()


@app.route("/attack", methods=['GET'])
def a():
    
    return render_template('attacker.html')
