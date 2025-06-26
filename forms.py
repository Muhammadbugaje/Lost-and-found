from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, SelectField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileAllowed

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('Personal', 'Personal'),
        ('Phone', 'Phone'),
        ('Clothing', 'Clothing'),
        ('Books', 'Books'),
        ('ID', 'ID'),
        ('Finance', 'Finance'),
        ('wearables', 'wearables'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    found_location = StringField('Found Location', validators=[DataRequired()])
    take_from_location = StringField('Take From Location', validators=[DataRequired()])
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Add Item')

class ClaimForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    reg_number = StringField('Registration Number', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField('Claim Item')