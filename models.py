from .exts import db
from sqlalchemy import CheckConstraint
from sqlalchemy.sql import func


user_sites = db.Table(
        "user_sites",
        db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
        db.Column('site_id', db.Integer, db.ForeignKey('site.id'), primary_key=True)
        )


site_subjects = db.Table(
        "site_subjects",
        db.Column('site_id', db.Integer, db.ForeignKey('site.id'), primary_key=True),
        db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True)
        )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    sites = db.relationship('Site', secondary=user_sites, backref='user', lazy='dynamic')

    def as_dict(self):
        return {
                "id": self.id,
                "username": self.username
                }


class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)

    galleries = db.relationship('Gallery', backref='site')
    subjects = db.relationship('Subject', secondary=site_subjects, backref='sites', lazy='dynamic')

    def as_dict(self):
        return {
                "id": self.id,
                "name": self.name,
                }


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(64), nullable=False)

    def as_dict(self):
        return {
                "id": self.id,
                "subject": self.subject,
                "connections_count": len(self.sites)
                }


class Gallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    sort = db.Column(db.Integer, CheckConstraint('sort >= 1'))
    private = db.Column(db.Boolean)
    edit_date = db.Column(db.DateTime, onupdate=func.now())             

    site_id = db.Column(db.Integer, db.ForeignKey('site.id'))

    photos = db.relationship('Photo', backref='gallery', lazy='dynamic')

    def as_dict(self):
        return {
                "id": self.id,
                "name": self.name,
                "description": self.description,
                "sort": self.sort,
                "edit_date": str(self.edit_date),
                "photos": [p.as_dict() for p in self.photos]
                }

    def photos_count(self):
        return len(self.photos)


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    sort = db.Column(db.Integer, CheckConstraint('sort >= 1'))
    edit_date = db.Column(db.DateTime, onupdate=func.now())

    gallery_id = db.Column(db.Integer, db.ForeignKey('gallery.id'))

    def as_dict(self):
        return {
                "id": self.id,
                "filename": self.filename,
                "description": self.description,
                "sort": self.sort,
                "edit_date": str(self.edit_date),
                }
