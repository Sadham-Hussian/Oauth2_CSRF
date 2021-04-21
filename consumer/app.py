import requests
from flask import Flask, redirect, render_template, session
from flask.globals import request
from flask.helpers import url_for
from flask_cors import CORS
import datetime

import settings
from models import User, db


app = Flask(__name__)
app.config.from_object(settings)
CORS(app)

db.init_app(app)

PROVIDER_BASE_URL = "http://127.0.0.1:5000/oauth"
CLIENT_ID = "5udiNw8knA8WoTLlhVNfJeNV"
CLIENT_SECRET = "Qn2X4znEUOd4LoyH0Jq7BnE25UWoDOBle1dkmHXc4CebMoQz"
BASE64_SECRET = "NXVkaU53OGtuQThXb1RMbGhWTmZKZU5WOlFuMlg0em5FVU9kNExveUgwSnE3Qm5FMjVVV29ET0JsZTFka21IWGM0Q2ViTW9Reg=="


def current_user() -> User:
    if 'consumer_login_id' in session:
        uid = session['consumer_login_id']
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
        session['consumer_login_id'] = user.id
        # if user is not just to log in, but need to head back to the auth page, then go for it
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect('/')

    return render_template('login.html')

@app.route('/consumer/oauth2/vulnerable/login', methods=['GET'])
def vulnerable_login():
    # This is implemented without the state parameter
    provider_url = f"{PROVIDER_BASE_URL}/authorize?response_type=code&scope=profile"
    redirect_uri = "&redirect_uri=http://localhost:4000/consumer/oauth2/vulnerable/callback"
    client_id = "&client_id=" + CLIENT_ID
    return redirect(provider_url + redirect_uri + client_id)

@app.route("/consumer/oauth2/vulnerable/callback", methods=['GET'])
def vulnerable_callback():
    code = request.args.get('code')
    if not code:
        return {"message": "Invalid code"}, 400
    
    url = f'{PROVIDER_BASE_URL}/token?grant_type=authorization_code'
    url = f'{PROVIDER_BASE_URL}/token?grant_type=authorization_code&redirect_uri=http://localhost:4000/consumer/oauth2/vulnerable/callback'
    headers = { 
        'Authorization': f'Basic {BASE64_SECRET}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = [('code', code)]
    response = requests.request('POST', url, data=data, headers=headers,)
    response_json = response.json()
    token = response_json.get('access_token', None)
    if not token:
        return response_json, 400

    associate_user_with_token(token)
    return response_json


@app.route('/consumer/oauth2/protected/login', methods=['GET'])
def protected_login():
    provider_url = f"{PROVIDER_BASE_URL}/authorize?response_type=code&scope=profile"

    redirect_uri = "&redirect_uri=http://localhost:4000/consumer/oauth2/protected/callback"
    client_id = "&client_id=" + CLIENT_ID
    state = str(datetime.datetime.now().timestamp())
    state_param = f"&state={state}"
    session['state'] = state
    return redirect(provider_url + redirect_uri + client_id + state_param)

@app.route("/consumer/oauth2/protected/callback", methods=['GET'])
def protected_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    stored_state = session.get('state', None)
    print(stored_state, state)
    if not state:
        return {"message": "Missing state - possible CSRF"}, 400

    if not state == stored_state:
        return {"message": "State mismatch - possible CSRF"}, 400
    if not code:
        return {"message": "Invalid code"}, 400

    url = f'{PROVIDER_BASE_URL}/token?grant_type=authorization_code&redirect_uri=http://localhost:4000/consumer/oauth2/protected/callback'
    headers = {
        'Authorization': f'Basic {BASE64_SECRET}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = [('code', code)]
    response = requests.request('POST', url, data=data, headers=headers,)
    response_json = response.json()
    print(response.text)
    token = response_json.get('access_token', None)
    if not token:
        return response_json, 400
    associate_user_with_token(token)
    return redirect('/')

