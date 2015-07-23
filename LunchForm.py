from flask.ext.wtf import Form
from wtforms.fields import StringField, SubmitField

class LunchForm(Form):
	submitter = StringField(u'Hi, my name is')
	food = StringField(u'and I ate')
	submit =  SubmitField(u'share my lunch details!')