"""
Initialization of application and api blueprints and other modules.
"""
from flask import Flask
from config import config
from flask_bootstrap import Bootstrap

bootstrap = Bootstrap()         # Styling of web interface.


def create_app(config_name='default', **config_overrides):
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])
    # Apply overrides
    app.config.update(config_overrides)
    # Override configurations **kwargs if any/
    config[config_name].init_app(app)

    bootstrap.init_app(app)

    # Register blueprints for restapi. All Restapi calls will be prefixed as
    # http(s)://<server_ip>:<server_port>/api/
    from .api import r_api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    # Register blueprints for web api. All Web calls will be prefixed as
    # http(s)://<server_ip>:<server_port>/web/
    from .web import web_api as web_blueprint
    app.register_blueprint(web_blueprint, url_prefix='/web')

    return app
