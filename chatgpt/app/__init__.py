from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from datetime import datetime

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'super-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)
    migrate.init_app(app, db)  

    from .models import User

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes import main
    from .auth import auth
    from .timetable import timetable

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')


    app.register_blueprint(timetable)

    # Register custom template filters
    @app.template_filter('date')
    def date_filter(value):
        if isinstance(value, str):
            value = datetime.strptime(value, '%Y-%m-%d')
        return value.strftime('%B %d, %Y')

    @app.template_filter('datetime')
    def datetime_filter(value):
        if isinstance(value, str):
            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return value.strftime('%b %d, %Y %I:%M %p')

    with app.app_context():
        from .models import User, Student, AttendanceRecord, TimetableEntry, LessonProgress
        db.create_all()

    return app
