import os

from werkzeug.serving import run_simple

from web.wsgi import application

if __name__ == '__main__':
    run_simple(
        hostname=os.getenv('FLASK_HOST', 'localhost'),
        port=int(os.getenv('FLASK_PORT', '5000')),
        application=application,
        use_reloader=True
    )
