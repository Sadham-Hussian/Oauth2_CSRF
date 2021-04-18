from flask import Flask, render_template, redirect
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
	return "Callback"


if __name__=='__main__':
	app.run(debug=True)