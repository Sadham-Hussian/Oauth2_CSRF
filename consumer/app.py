from flask import Flask, render_template, redirect, session
from flask.globals import request
from flask_cors import CORS
import requests

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

CORS(app)

PROVIDER_BASE_URL = "http://localhost:5000/provider/oauth2/vulnerable"
PROVIDER_PROTECTED_BASE_URL = "http://localhost:5000/provider/oauth2/protected"
@app.route('/')
def index():
	return "Hello World"

@app.route('/consumer/login', methods=['GET'])
def login_webpage():
	return render_template('login.html')

@app.route('/consumer/oauth2/vulnerable/login', methods=['GET'])
def vulnerable_login():
	provider_url = "http://localhost:5000/provider/oauth2/vulnerable/login"
	redirect_uri = "redirect_uri=http://localhost:4000/consumer/oauth2/vulnerable/callback"
	client_id = "&client_id=" + "consumer"
	return redirect(provider_url + "?" + redirect_uri + client_id)

@app.route("/consumer/oauth2/vulnerable/callback", methods=['GET'])
def vulnerable_callback():
	code = request.args.get('code')
	if not code:
		return {"message": "Invalid code"}, 400
	get_access_token = requests.post(f'{PROVIDER_BASE_URL}/token', )
	return get_access_token.json()


@app.route('/consumer/oauth2/protected/login', methods=['GET'])
def protected_login():
	provider_url = "http://localhost:5000/provider/oauth2/protected/login"
	redirect_uri = "redirect_uri=http://localhost:4000/consumer/oauth2/protected/callback"
	client_id = "&client_id=" + "consumer"
	state = "&state=abcd"
	session['state'] = 'abcd'
	return redirect(provider_url + "?" + redirect_uri + client_id + state)

@app.route("/consumer/oauth2/protected/callback", methods=['GET'])
def protected_callback():
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


if __name__=='__main__':
	app.run(debug=True)