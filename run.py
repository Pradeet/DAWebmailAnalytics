from flask import Flask, jsonify, request, make_response
from flask.ext.httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, url_for, redirect
from flask.ext.wtf import Form
from wtforms.fields import StringField, SubmitField
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dawebmailers_v1.0.db'
app.config['SECRET_KEY'] = 'HALO'

db = SQLAlchemy(app)
auth = HTTPBasicAuth()

# this is for CSS
def get_resource_as_string(name, charset='utf-8'):
    with app.open_resource(name) as f:
        return f.read().decode(charset)
app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string

class User(db.Model):
	#id = db.Column(db.Integer, primary_key = True)
	u_studentID = db.Column(db.String(63),  primary_key = True)
	u_blue = db.Column(db.String(127))
	u_registrationTime = db.Column(db.String(127))

class PhoneDetails(db.Model):
	p_studentID = db.Column(db.String(63),  primary_key = True)
	p_brand = db.Column(db.String(127))
	p_product = db.Column(db.String(127))
	p_model = db.Column(db.String(127))
	p_applist = db.Column(db.Text)
	p_screensize = db.Column(db.String(127))

class LoginDetails(db.Model):
	l_studentID = db.Column(db.String(63), primary_key = True)
	l_timestamp = db.Column(db.String(511))
	l_type = db.Column(db.String(63))
	l_connection = db.Column(db.String(63))
	l_connectiondetails = db.Column(db.String(127))

class LocationDetails(db.Model):
	c_studentID = db.Column(db.String(63), primary_key = True)
	c_timestamp = db.Column(db.String(63)) 
	c_wifiname = db.Column(db.String(63))
	c_ipaddress = db.Column(db.String(63))
	c_subnet = db.Column(db.String(63))

@auth.get_password
def get_password(username):
	if username == 'dawebmail' :
		return 'machoman'
	return None

@auth.error_handler
def unauthorized():
	return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.route('/')
def root():
	users = User.query.all()
	logins = LoginDetails.query.all()

	return render_template('index.html', users = users)

@app.route('/heartbeat')
def heartbeat():
	return jsonify(dawebmail=True)

@app.route('/v1/student', methods = [u'POST', u'GET'])
@auth.login_required
def student():
	if request.method == u'POST':
		json_SID = request.get_json().get('u_studentid', '')
		json_blue = request.get_json().get('u_blue', '')
		json_regTime = request.get_json().get('u_regTime', '')
		users = User.query.all()
		for user in users :
			if user.u_studentID == json_SID :
				tochange = False
				if json_blue != user.u_blue :
					user.u_blue = json_blue
					tochange = True
				if json_regTime != user.u_registrationTime :
					user.u_registrationTime = json_regTime
					tochange = True
				
				#db.session.query(User).filter(User.studentID == json_SID).update({'blue':user.blue})
				if tochange == True :
					db.session.commit()
				return jsonify(metadata = 'already exists', updated = tochange)	

		user = User()
		user.u_studentID = json_SID
		user.u_blue = json_blue
		user.u_registrationTime = json_regTime
		db.session.add(user)
		db.session.commit()

		return jsonify(metadata = 'created user successfully')
	if request.method == u'GET':
		jsonData = []
		users = User.query.all()
		for user in users :
			jsonData.append({'u_studentID':user.u_studentID, 'u_blue':user.u_blue, 'u_registrationTime':user.u_registrationTime})

		return jsonify(results = jsonData)

@app.route('/v1/login', methods = [u'POST', u'GET'])
@auth.login_required
def login():
	if request.method == 'POST':
		loginDetails = LoginDetails()

		loginDetails.l_studentID = request.get_json().get('l_studentID','')
		loginDetails.l_timestamp = request.get_json().get('l_timestamp','')
		loginDetails.l_type = request.get_json().get('l_type','')
		loginDetails.l_connection = request.get_json().get('l_connection','')
		loginDetails.l_connectiondetails = request.get_json().get('l_connectiondetails','')
		
		db.session.add(loginDetails)
		db.session.commit()

		return jsonify(status=True)
	if request.method == 'GET':
		jsonData = []
		loginDetails = LoginDetails.query.all()
		for loginDetail in loginDetails:
			jsonData.append({'l_studentID':loginDetail.l_studentID, 'l_timestamp':loginDetail.l_timestamp, 'l_type':loginDetail.l_type, 'l_connection':loginDetail.l_connection, 'l_connectiondetails':loginDetail.l_connectiondetails})

		return jsonify(results = jsonData)

@app.route('/v1/location', methods = [u'POST', u'GET'])
@auth.login_required
def location():
	if request.method == 'POST':
		locationDetails = LocationDetails()

		locationDetails.c_studentID = request.get_json().get('c_studentID','')
		locationDetails.c_timestamp = request.get_json().get('c_timestamp','')
		locationDetails.c_wifiname = request.get_json().get('c_wifiname','')
		locationDetails.c_ipaddress = request.get_json().get('c_ipaddress','')
		locationDetails.c_subnet = request.get_json().get('c_subnet','')

		db.session.add(loginDetails)
		db.session.commit()

		return jsonify(status = True)

	if request.method == 'GET' :
		jsonData = []
		locationDetails = LocationDetails.query.all()
		for location in locationDetails :
			jsonData.append({'c_studentID':location.c_studentID, 'c_timestamp':location.c_timestamp,'c_wifiname':location.c_wifiname,'c_ipaddress':location.c_ipaddress, 'c_subnet':location.c_subnet})

		return jsonify(results = jsonData)

@app.route('/v1/phone',  methods = [u'POST', u'GET'])
@auth.login_required
def phone():
	if request.method == 'POST' :
		phoneDetails = PhoneDetails()
		phoneDetails.p_studentID = request.get_json().get('p_studentID','')
		phoneDetails.p_brand = request.get_json().get('p_brand','')
		phoneDetails.p_product = request.get_json().get('p_product','')
		phoneDetails.p_model = request.get_json().get('p_model','')
		phoneDetails.p_applist = request.get_json().get('p_applist','')
		phoneDetails.p_screensize = request.get_json().get('p_screensize','')

		db.session.add(phoneDetails)
		db.session.commit()

		return jsonify(status = True)

	if request.method == 'GET' :
		jsonData = []
		phoneDetails = PhoneDetails.query.all()
		for phoneDetail in phoneDetails :
			jsonData.append({'p_studentID':phoneDetail.p_studentID, 'p_brand':phoneDetail.p_brand,'p_product':phoneDetail.p_product,'p_model':phoneDetail.p_model,'p_applist': phoneDetail.p_applist,'p_screensize':phoneDetail.p_screensize})

		return jsonify(results = jsonData)

if __name__ == '__main__' :
	db.create_all()
	app.run(host="192.168.150.1",port=8000, debug=True)