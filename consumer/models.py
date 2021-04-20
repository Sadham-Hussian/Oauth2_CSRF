from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    oauth2_token = db.Column(db.String(512))

    def __str__(self):
        return self.username

    def get_user_id(self):
        return self.id

