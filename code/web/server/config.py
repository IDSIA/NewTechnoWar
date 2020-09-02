from os import environ


class Config:
    """Set Flask configuration vars from .env file."""

    # General Config
    FLASK_HOST = environ.get('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = environ.get('FLASK_PORT', '5000')
    FLASK_DEBUG = environ.get('FLASK_DEBUG', '0') == '1'
    FLASK_ENV = environ.get('FLASK_ENV', 'production')


conf = Config()
