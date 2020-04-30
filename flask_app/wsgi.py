"""
Gunicorn entry point
"""
from flask_app.run import app

if __name__ == '__main__':
    app.run()
