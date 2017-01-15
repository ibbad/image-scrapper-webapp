"""
This module contains the forms used for setting up web interfaces.
"""


from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import input_required


class GetURLsForm(FlaskForm):
    """
    Blueprint of form for getting URL from the user.
    """
    url_field = StringField('Enter url', validators=[input_required()])
    show = SubmitField('Show')
    download = SubmitField('Download')


class ShowLinksForm(FlaskForm):
    """
    Blueprint of form for getting URL from the user.
    """
    download_url_list = SubmitField('Download URL list')
    download_images = SubmitField('Download Images')
