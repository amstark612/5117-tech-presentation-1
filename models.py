import enum
import datetime as dt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy import Index, types

ALLOWED_TAGS = [
    'b',
    'br',
    'div',
    'i',
    'li',
    'ol',
    'strong',
    'u',
    'ul',
    'underline'
]

db = SQLAlchemy()

ALLOWED_FILE_TYPES = [
    'gif',
    'jpeg',
    'jpg',
    'png'
]

class TSVector(types.TypeDecorator):
    impl = TSVECTOR

class MediaType(enum.Enum):
    jpg = 1
    png = 2
    gif = 3
    mp3 = 4
    mp4 = 5

class UpvotedAssociation(db.Model):
    user_id = db.Column(db.Text, db.ForeignKey('user.id'), primary_key=True, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True, nullable=False)
    num_votes = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref=db.backref('upvoted', cascade='all, delete-orphan'))
    post = db.relationship('Post', backref=db.backref('upvoted', cascade='all, delete-orphan'))

class User(db.Model):
    id = db.Column(db.Text, primary_key=True, nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    display_name = db.Column(db.String(30))
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return '<User(username=%s)>' % self.username

    upvoted = association_proxy('upvoted', 'post', creator=lambda post: UpvotedAssociation(post=post))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)

    creator_id = db.Column(db.Text, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User", backref=db.backref('posts', lazy=True, cascade='all, delete-orphan'))

    created_at = db.Column(db.DateTime(), default=dt.datetime.now(), nullable=False)
    title = db.Column(db.String(140), nullable=False)
    body = db.Column(db.Text, nullable=False)
    num_votes = db.Column(db.Integer, default=0)

    # dunno if we'll use this, putting it here in case we do so we don't have to run a migration
    media = db.Column(db.LargeBinary)
    media_type = db.Column(db.Enum(MediaType))

    # trying new method for uploading CTN-TODO: this is deprecated but we didn't want to drop our db so...yeah.
    img = db.Column(db.Text)

    __tsvector__ = db.Column(TSVector(), db.Computed("to_tsvector('english', title || ' ' || body)", persisted=True))
    __table_args__ = (Index('ix_post__tsvector__', __tsvector__, postgresql_using='gin'),)

    def __repr__(self):
        return '<Post(creator_id=%s, title=%s)>' % (self.creator_id, self.title)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)

    created_at = db.Column(db.DateTime(), default=dt.datetime.now(), nullable=False)
    body = db.Column(db.Text, nullable=False)

    creator_id = db.Column(db.Text, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('comments', lazy=True, cascade='all, delete-orphan'))

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    post = db.relationship('Post', backref=db.backref('comments', lazy=True, order_by=created_at, cascade='all, delete-orphan'))

    # dunno if we'll use this, putting it here in case we do so we don't have to run a migration
    num_votes = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<Comment(creator_id=%s, post_id=%s>' % (self.creator_id, self.post_id)
