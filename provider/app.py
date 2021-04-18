from flask import Flask, redirect, request, render_template
from flask_cors import CORS
import random
import string
import json

app = Flask(__name__)
CORS(app)

DB = {}

@app.route('/')
def index():
	return "Oauth provider server"

@app.route("/provider/oauth2/vulnerable/login", methods=['GET','POST'])
def auth():
	if request.method == "GET":
		redirect_uri = request.args.get('redirect_uri')
		client_id = request.args.get('client_id')
		return render_template('authorise.html', redirect_uri=redirect_uri)
	elif request.method == "POST":
		redirect_uri = request.args.get('redirect_uri')
		code = ''.join((random.choice(string.ascii_letters + string.digits) for _ in range(32)))
		return redirect(redirect_uri + '?code=' + code)

@app.route("/provider/oauth2/vulnerable/token", methods=['POST'])
def token():
	access_token = ''.join((random.choice(string.ascii_letters + string.digits) for _ in range(32)))
	response = {
		"access_token": access_token,
		"token_type": "bearer"
	}
	return json.dumps(response)

@app.route("/provider/vulnerable/userinfo", methods=['GET'])
def userinfo():
	info = {
		"username": "test",
		"email": "test@gmail.com",
		"ph_no": "+91-6383440981",
	}
	return json.dumps(info)

@app.route("/provider/oauth2/protected/login", methods=['GET','POST'])
def auth_protected():
	if request.method == "GET":
		redirect_uri = request.args.get('redirect_uri')
		client_id = request.args.get('client_id')
		return render_template('authorise.html', redirect_uri=redirect_uri)
	elif request.method == "POST":
		redirect_uri = request.args.get('redirect_uri')
		
		code = ''.join((random.choice(string.ascii_letters + string.digits) for _ in range(32)))
		return redirect(redirect_uri + '?code=' + code + '&state=abcd')


if __name__=='__main__':
	app.run(debug=True)