from flask import Flask, jsonify, request, make_response
from flask.ext.httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, redirect, url_for
from socket import gethostname

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dawebmailers_v4.db'
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

class ActionDetails(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    a_studentID = db.Column(db.String(63))
    a_action = db.Column(db.String(511))
    a_connection = db.Column(db.String(127))
    a_connectionDetails = db.Column(db.String(127))
    a_timeStamp = db.Column(db.String(127))
    a_timeTaken = db.Column(db.String(127))
    a_success = db.Column(db.String(15)) #either true or false
    
    def __init__(self, a_studentID, a_action, a_connection, a_connectionDetails, a_timeStamp, a_timeTaken, a_success):
        self.a_studentID = a_studentID
        self.a_action = a_action
        self.a_connection = a_connection
        self.a_connectionDetails = a_connectionDetails
        self.a_timeStamp = a_timeStamp
        self.a_timeTaken = a_timeTaken
        self.a_success = a_success

class FeedbackDetails(db.Model):
	id = db.Column(db.Integer, primary_key = True, autoincrement = True)
	f_studentID = db.Column(db.String(63))
	f_feedback = db.Column(db.Text)
	f_timestamp = db.Column(db.String(511))

@auth.get_password
def get_password(username):
    if username == 'dawebmail' :
        return 'machoman'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.route('/')
@auth.login_required
def root():
    users = User.query.all()
    return render_template('index.html', users = users)

@app.route('/heartbeat')
def heartbeat():
    return jsonify(dawebmail=True)

@app.route('/v1/register', methods = [u'POST', u'GET'])
@auth.login_required
def register():
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
            jsonData.append({'id':user.id,'u_studentID':user.u_studentID, 'u_blue':user.u_blue, 'u_registrationTime':user.u_registrationTime})

        return jsonify(results = jsonData)

@app.route('/v1/action', methods = [u'POST', u'GET'])
@auth.login_required
def login():
    if request.method == 'POST':
        for jsonData in request.json :

            json_studentID = jsonData['a_studentID']
            json_action = jsonData['a_action']
            json_connection = jsonData['a_connection']
            json_connectiondetails = jsonData['a_connectionDetails']
            json_timestamp = jsonData['a_timeStamp']
            json_timetaken = jsonData['a_timeTaken']
            json_success = jsonData['a_success']
            actionDetails = ActionDetails(json_studentID, json_action, json_connection, json_connectiondetails, json_timestamp, json_timetaken, json_success)
            db.session.add(actionDetails)

        db.session.commit()
        return "[{'metdata':'metdata'},{'status':'true'}]"

    if request.method == 'GET':
        jsonData = []
        actionDetails = ActionDetails.query.all()
        for actionDetail in actionDetails:
            jsonData.append({'id':actionDetail.id,'a_studentID':actionDetail.a_studentID, 'a_action':actionDetail.a_action, 'a_connection':actionDetail.a_connection, 'a_connectionDetails':actionDetail.a_connectionDetails, 'a_timeStamp':actionDetail.a_timeStamp, 'a_timeTaken':actionDetail.a_timeTaken, 'a_success':actionDetail.a_success})

        return jsonify(results = jsonData)

@app.route('/v1/action/<username>')
@auth.login_required
def action(username):
    user_actionDetails = db.session.query(ActionDetails).filter(ActionDetails.a_studentID.in_([username])).order_by("a_action desc").all()
    return render_template('action.html', username = username, details = user_actionDetails)

@app.route('/phone')
@auth.login_required
def phone_all():
    phones = db.session.query(PhoneDetails).order_by("p_studentID desc").all()
    return render_template('phone.html', phones = phones)

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
            jsonData.append({'id':phoneDetail.id,'p_studentID':phoneDetail.p_studentID, 'p_brand':phoneDetail.p_brand,'p_product':phoneDetail.p_product,'p_model':phoneDetail.p_model,'p_applist': phoneDetail.p_applist,'p_screensize':phoneDetail.p_screensize})

        return jsonify(results = jsonData)

@app.route('/v1/feedback', methods = ['GET','POST'])
@auth.login_required
def feedback():
	if request.method == 'POST' :
		for jsonData in request.json :
			json_studentID = jsonData['f_studentID']
			json_feedback = jsonData['f_feedback']
			json_timestamp = jsonData['f_timestamp']
			
			feedbackDetails = FeedbackDetails()
			feedbackDetails.f_studentID = json_studentID
			feedbackDetails.f_feedback  = json_feedback
			feedbackDetails.f_timestamp = json_timestamp
			db.session.add(feedbackDetails)
		db.session.commit()
		return '[{"status":"True"}]'
	if request.method == 'GET' :
		jsonData = []
        feedbackDetails = FeedbackDetails.query.all()
        #for feedbackDetail in feedbackDetails :
            #jsonData.append({'id':feedbackDetail.id, 'f_studentID':feedbackDetail.f_studentID,'f_feedback':feedbackDetail.f_feedback, 'f_timestamp':feedbackDetail.f_timestamp})
        #return jsonify(results = jsonData)
        return render_template('feedback.html', feedbacks = feedbackDetails)

@app.route('/v1/delete/<task>/<int:del_id>')
@auth.login_required
def delete(task, del_id):

    if task == 'phone':
        PhoneDetails.query.filter_by(id = del_id).delete()
    if task == 'student':
        User.query.filter_by(id = del_id).delete()
    if task == 'feedback':
        FeedbackDetails.query.filter_by(id = del_id).delete()
    if task == 'action':
        ActionDetails.query.filter_by(id = del_id).delete()

    db.session.commit()
    return redirect(url_for(task))

if __name__ == '__main__' :
    db.create_all()
    if 'liveconsole' not in gethostname():
        app.run(host="192.168.150.1",port=8080, debug=True)