import enum
import datetime as dt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy

db = SQLAlchemy()

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
    post = db.relationship('Post')

class User(db.Model):
    id = db.Column(db.Text, primary_key=True, nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    display_name = db.Column(db.String(30))
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    # uv = db.relationship('Post', secondary=upvoted, lazy='subquery', backref=db.backref('users', lazy=True))

    def __repr__(self):
        return '<User(username=%s)>' % self.username

    upvoted = association_proxy('upvoted', 'post', creator=lambda post: UpvotedAssociation(post=post))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)

    creator_id = db.Column(db.Text, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User", backref=db.backref('posts', lazy=True))

    created_at = db.Column(db.DateTime(), default=dt.datetime.now(), nullable=False)
    title = db.Column(db.String(140), nullable=False)
    body = db.Column(db.Text, nullable=False)
    num_votes = db.Column(db.Integer, default=0)

    # dunno if we'll use this, putting it here in case we do so we don't have to run a migration
    media = db.Column(db.LargeBinary)
    media_type = db.Column(db.Enum(MediaType))

    def __repr__(self):
        return '<Post(creator_id=%s, title=%s)>' % (self.creator_id, self.title)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)

    creator_id = db.Column(db.Text, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    post = db.relationship('Post', backref=db.backref('comments', lazy=True))

    created_at = db.Column(db.DateTime(), default=dt.datetime.now(), nullable=False)
    body = db.Column(db.Text, nullable=False)

    # dunno if we'll use this, putting it here in case we do so we don't have to run a migration
    num_votes = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<Comment(creator_id=%s, post_id=%s>' % (self.creator_id, self.post_id)

#################################################
##### LEAVE THIS HERE SO NO ERRORS IN VIEW ######
#################################################



'''
####### EXAMPLE 1
set up tables easily, accessing table row as object, object methods
'''

class User(db.Model):
    id = db.Column(db.Text, primary_key=True, nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    display_name = db.Column(db.String(30))
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    birthday = db.Column(db.Date)
    # uv = db.relationship('Post', secondary=upvoted, lazy='subquery', backref=db.backref('users', lazy=True))

    def __repr__(self):
        return '<User(username=%s)>' % self.username

    upvoted = association_proxy('upvoted', 'post', creator=lambda post: UpvotedAssociation(post=post))

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

db.create_all()

people = User.query.all()

for person in people:
    print(person.first_name)
    print(person.full_name)


'''
####### EXAMPLE 2
chaining variable number of query parameters, aggregation, etc without defining lots
of custom functions with minute differences
'''

User.get(id='1').first()
User.get(id='1', last_name='Johnson').first()

User.query.filter_by(last_name='Johnson').order_by(User.last_name.asc())
User.query.filter_by(last_name='Johnson').order_by(User.last_name.desc())

'''
####### EXAMPLE 3
select different columns without defining a different function for each column, for each table
'''
info = User.query.with_entities(User.birthday, User.first_name).filter_by(username='ted_lasso').first()


'''
####### EXAMPLE 4
get related entities very easily!
'''
person = User.query.filter_by(username='ted_lasso')
posts = person.posts
comments = person.comments

for post in posts:
    print(post.body)

for comment in comments:
    print(comment.body)