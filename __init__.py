import os
from .init_db import init_db


def create_app():
    from flask import Flask

    app = Flask(__name__)
    basedir = os.path.abspath(os.path.dirname(__file__))

    app.config.from_mapping(
            SECRET_KEY=os.getenv('SECRET_KEY'),
            UPLOAD_FOLDER=os.path.join(basedir, 'pictures/'),
            SQLALCHEMY_DATABASE_URI=\
                    'sqlite:///' + os.path.join(basedir, 'master.db'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False
        )

    from .views import bp as views_bp
    app.register_blueprint(views_bp)

    from .errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from .exts import db, migrate
    db.init_app(app)
    migrate.init_app(app, db)

    from .models import User, Gallery, Photo
    
    with app.app_context():
        init_db()
    return app


