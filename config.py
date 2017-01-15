"""
Basic configuration for the app
"""
import os
from helpers.helper_functions import generate_secret_key


class Config:
    """
    Default configuration parameters
    """
    # Image extensions that should be looked for in the web page.
    IMAGE_EXTENSIONS = ['.jpg', '.png', '.svg', '.gif', '.jpeg']
    SECRET_KEY = os.environ.get('SECRET_KEY') or generate_secret_key()
    FILES_DIR = 'files/'
    TEMP_SUBFOLDER = 'tmp/'     # Inside the FILES_DIR
    APP_WD = os.getcwd()        # Application working directory
    # Possible protocols for loading images.
    PROTOCOLS = {
        'http': 'http://',
        'https': 'https://',
        'data-uri': 'data:image/'
    }
    URL_REGEX = r"_^(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?!10(?:\.\d{1,3}){3})(?!127(?:\.\d{1,3}){3})(?!169\.254(?:\.\d{1,3}){2})(?!192\.168(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\x{00a1}-\x{ffff}0-9]+-?)*[a-z\x{00a1}-\x{ffff}0-9]+)(?:\.(?:[a-z\x{00a1}-\x{ffff}0-9]+-?)*[a-z\x{00a1}-\x{ffff}0-9]+)*(?:\.(?:[a-z\x{00a1}-\x{ffff}]{2,})))(?::\d{2,5})?(?:/[^\s]*)?$_iuS"

    SSL_DISABLE = False
    # Number of links shown per page
    LINKS_PER_PAGE = 30

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    WTF_CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,

    'default': DevelopmentConfig
}
