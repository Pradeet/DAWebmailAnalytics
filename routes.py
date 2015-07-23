from flask import render_template, url_for, redirect

@app.route('/')
def root():
	lunches = Lunch.query.all()
	form = LunchForm()
	return render_template('index.html', form = form, lunch = lunches)

@app.route('/new', methods = [u'POST'])
def newLunch():
	form = LunchForm()
	if form.validate_on_submit():
		lunch = Lunch()
		form.populate_obj(lunch)
		db.session.add(lunch)
		db.session.commit()
	return redirect(url_for('root'))