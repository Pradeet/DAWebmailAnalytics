from flask import Flask, jsonify, request, make_response
from flask.ext.httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from socket import gethostname

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dawebmailers_v1.1.db'
app.config['SECRET_KEY'] = 'HALO'

db = SQLAlchemy(app)
auth = HTTPBasicAuth()

# this is for CSS
def get_resource_as_string(name, charset='utf-8'):
    with app.open_resource(name) as f:
        return f.read().decode(charset)
app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    u_studentID = db.Column(db.String(63))
    u_blue = db.Column(db.String(127))
    u_registrationTime = db.Column(db.String(127))

class PhoneDetails(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    p_studentID = db.Column(db.String(63))
    p_brand = db.Column(db.String(127))
    p_product = db.Column(db.String(127))
    p_model = db.Column(db.String(127))
    p_applist = db.Column(db.Text)
    p_screensize = db.Column(db.String(127))

class LoginDetails(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    l_studentID = db.Column(db.String(63))
    l_timestamp = db.Column(db.String(511))
    l_type = db.Column(db.String(63))
    l_connection = db.Column(db.String(63))
    l_connectiondetails = db.Column(db.String(127))

class LocationDetails(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    c_studentID = db.Column(db.String(63))
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
    return render_template('index.html', users = users)

@app.route('/heartbeat')
def heartbeat():
    return jsonify(dawebmail=True)

@app.route('/v1/student', methods = [u'POST', u'GET'])
@auth.login_required
def student():
    if request.method == u'POST':
        jsonData = request.json

        json_SID = jsonData['u_studentid']
        json_blue = jsonData['u_blue']
        json_regTime = jsonData['u_regTime']
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

        for jsonData in request.json :

            json_studentID = jsonData['l_studentID']
            json_timestamp = jsonData['l_timestamp']
            json_type = jsonData['l_type']
            json_connection = jsonData['l_connection']
            json_connectiondetails = jsonData['l_connectiondetails']

            loginDetails = LoginDetails()
            loginDetails.l_studentID = json_studentID
            loginDetails.l_timestamp = json_timestamp
            loginDetails.l_type = json_type
            loginDetails.l_connection = json_connection
            loginDetails.l_connectiondetails = json_connectiondetails
            
            db.session.add(loginDetails)

        db.session.commit()
        return "[{'metdata':'metdata'},{'status':'true'}]"
        
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

        for jsonData in request.json :
         
            json_studentID = jsonData['c_studentID']
            json_timestamp = jsonData['c_timestamp']
            json_wifiname = jsonData['c_wifiname']
            json_ipaddress = jsonData['c_ipaddress']
            json_subnet = jsonData['c_subnet']

            locationDetails = LocationDetails()
            locationDetails.c_studentID = json_studentID
            locationDetails.c_timestamp = json_timestamp
            locationDetails.c_wifiname = json_wifiname
            locationDetails.c_ipaddress = json_ipaddress
            locationDetails.c_subnet = json_subnet

            db.session.add(locationDetails)
        
        db.session.commit()

        return "[{'metdata':'metdata'},{'status':'true'}]"

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
        for jsonData in request.json : 
            json_studentID = jsonData['p_studentID']
            json_brand = jsonData['p_brand']
            json_product = jsonData['p_product']
            json_model = jsonData['p_model']
            json_applist = jsonData['p_applist']
            json_p_screensize = jsonData['p_screensize']

            phoneDetails = PhoneDetails()
            phoneDetails.p_studentID = json_studentID
            phoneDetails.p_brand = json_brand
            phoneDetails.p_product = json_product
            phoneDetails.p_model = json_model
            phoneDetails.p_applist = json_applist
            phoneDetails.p_screensize = json_p_screensize

            db.session.add(phoneDetails)
        db.session.commit()

        return "[{'metdata':'metdata'},{'status':'true'}]"

    if request.method == 'GET' :
        jsonData = []
        phoneDetails = PhoneDetails.query.all()
        for phoneDetail in phoneDetails :
            jsonData.append({'p_studentID':phoneDetail.p_studentID, 'p_brand':phoneDetail.p_brand,'p_product':phoneDetail.p_product,'p_model':phoneDetail.p_model,'p_applist': phoneDetail.p_applist,'p_screensize':phoneDetail.p_screensize})

        return jsonify(results = jsonData)

if __name__ == '__main__' :
    db.create_all()
    if 'liveconsole' not in gethostname():
		app.run(host="192.168.150.1",port=8080, debug=True)