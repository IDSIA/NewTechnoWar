"""Initialize application"""
from flask import Flask

from web.server.config import conf


def create_app():
    """Construct the core application."""
    app = Flask(
        __name__,
        instance_relative_config=False,
        template_folder="templates",
        static_folder="static"
    )

    # Application Configuration
    app.config.from_object(conf)

    with app.app_context():
        # Import parts of our application
        from . import routes
        app.register_blueprint(routes.main_bp)

        return app
