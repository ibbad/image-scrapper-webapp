"""
Initialize blueprint for Restapi module for application.
"""
from flask import Blueprint

r_api = Blueprint('r_api', __name__)

# Setup the logger
import logging
from logging.handlers import RotatingFileHandler

api_logger = logging.getLogger(__name__)
api_logger.setLevel(logging.INFO)

# Formatter for logs.
api_log_format = logging.Formatter('%(asctime)s - %(name)s - '
                                      '%(levelname)s - %(message)s')

# Setup FileHandler for the logs.
api_log_fh = RotatingFileHandler('logs/restapi.log', maxBytes=1000000,
                                 backupCount=5)
api_log_fh.setLevel(logging.INFO)
api_log_fh.setFormatter(api_log_format)

# Setup StreamHandler for important logs.
api_log_stream = logging.StreamHandler()
api_log_stream.setLevel(logging.ERROR)

# Add handlers to the logger.
api_logger.addHandler(api_log_fh)
api_logger.addHandler(api_log_stream)

from . import views
