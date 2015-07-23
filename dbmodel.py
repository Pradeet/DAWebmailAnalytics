
class Lunch(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	submitter = db.Column(db.string(63))
	food = db.Column(db.string(255))