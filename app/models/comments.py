from sqlalchemy.orm import backref

from app.extensions import db
from datetime import datetime

class Comment(db.Model):

     __tablename__ = 'comments'

     id = db.Column(db.Integer, primary_key=True)
     article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
     author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
     content = db.Column(db.Text, nullable=False)
     created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
     updates_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
     parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
     replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id], lazy=True))