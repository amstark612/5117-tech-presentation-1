# Eager/Lazy Loading

## What is eager and lazy loading?
Unless your application is as simple as, say, storing surveys in a database such as in Homework 1, you will always have multiple entities (tables) that are related in some way. For example, in our project, a `Post` is written by a `User` and may have many `Comments`.
SQLAlchemy needs to know whether it should fetch the User who authored the `Post` and its `Comment`s when it fetches the `Post` - it needs to know whether it should *eager* load the entities related to the `Post`. In most cases, you probably want to *lazy* load - fetch the `Post` only.

### Advantages/Disadvantages
On one hand, every trip to the disc takes an eon and a half. The interest of your user is rapidly declining as your application is retrieving information, so you want to make as few trips as possible. So why not load all relations at once? Because any advantage gained by limiting the number of trips to the disc may be negated by the time it takes to transfer that much data back as well as the time it takes to serialize all that data.

## Lazy load by default
Generally, you will want tell SQLAlchemy to lazy load relations by default:

```
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)

    creator_id = db.Column(db.Text, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    post = db.relationship('Post', backref=db.backref('comments', lazy=True))

    created_at = db.Column(db.DateTime(), default=dt.datetime.now(), nullable=False)
    body = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<Comment(creator_id=%s, post_id=%s>' % (self.creator_id, self.post_id)
```

Here, we told SQLAlchemy *not* to load the associated `Post` and `User` when loading the `Comment`. Imagine if we were to set it to eager-load the `Post` associated with a `Comment` by default. If we were going to load a page for a `Post` and all the `Comment`s that belong to it, we would get a separate copy of the same `Post` for every single `Comment` that belongs to it! That is a lot of wasted space and wasted time.

### Example
What does this mean in practice?

```
comment = Comment.get(1)
print(f'The author of this comment is {comment.user.username}')

# The above statements translate to the following SQL expressions, which makes two trips to the database:

SELECT *
FROM comment
WHERE id = 1;

-- returns a row that includes a user_id, which we will pretend is 111

SELECT *
FROM user
WHERE id = 111;
```

## Eager load manually - Join!
Sometimes, though, it makes sense to eager load relations. If you were to visit the page for an individual `Post` where you want to display all of its `Comment`s, you would know beforehand that you want all of the comments. You could tell SQLAlchemy to manually load the `Post` and all of its `Comments` at the time of the query:

```
post = Post.query\
           .filter_by(id=1)\
           .options(db.joinedload(Post.comments))\
           .first()

# The statement above translates to the following SQL, which only makes one trip to the database 
# and stores the comments in the comments attribute of the Post object:

SELECT *
FROM post
LEFT JOIN comment ON comment.post_id = post.id
WHERE post.id = 1;
```

We would like to note, once again, how convenient it is that the ORM translates this to objects for us. It is not neccessary to grab the row that describes the `Post` and create a new `Post` object, then grab all the rows that describe `Comments` and create new `Comment` objects, and then put all of those `Comment` objects into a list, and then assign that list to `post.comments`.

# The N+1 Problem, with a capital P
Another instance where eager loading makes great sense happens when you have a many-to-many relation. In our previous example, a single `Post` may have many `Comment`s, but a `Comment` only belongs to one `Post`. What if we were to retrieve all the `Comment`s added within the last 10 days, and we wanted to see the `Post`s they belong to?

If 100 `Comment`s were added in the last 10 days, this would make 101 (or, N+1) trips to the database, even if some of those `Comment`s belong to the same post:

```
for comment in Comment.query.filter(Comment.created_at > (date.today() - timedelta(days=10))).all():
    print(comment.Post)

# This makes a trip to the database to get the comments:
SELECT *
FROM comment
WHERE created_at > '2022-03-14';

# And then 100 additional trips to the database to retrieve the posts! 
# It would be better to include the Posts in our initial query:

# joining any table by specifying join conditions:
Comment.query.filter(Comment.created_at > (date.today() - timedelta(days=10))).join(Post, Post.id == Comment.post_id).all()

# if you have defined your relationship on your models, you do not need to specify join conditions:
Comment.query.filter(Comment.created_at > (date.today() - timedelta(days=10))).options(db.joinedload(Post)).all()
```

## Eager loading selected columns (raw SQL) & subqueries
What about more complex queries? Sometimes, you might only want selected attributes of related entities. For example, when we display a `Post`, we also want to display the `username` of the author and the number of `Comment`s that have been added to it. In all honesty, this is easier using raw SQL - like many frameworks, ORMs are great up until you want to deviate from its opinion. ORMs don't want you to break the model - every row, or relation, should map to one object. Once you start pulling multiple columns from multiple tables, you no longer have a Model.

It's important to note, here, that any complete and performant application using an ORM must also be able to execute raw SQL. It is unrealistic to imagine our site having thousands of `Post`s and making two additional trips to the database (once to get the number of `Comment`s and another to get the author's `username`) *for each `Post`*. No one would ever use our site.

Anyway, if the data you're trying to retrieve does not span multiple models, you can use subqueries. For example, maybe you only want the `Post` with the more than 10 `Comment`s - you're still retrieving a `Post` object in the end, you just want to select the `Post` based on its related entities.

```
subquery = db.session.query(
    Post.id,
    db.func.count(Comment.id).label('num_comments'))\
    .group_by(Post.id)\
    .subquery()

# Remember, here, subquery is like typing your search terms into the Google search bar without actually hitting 
# enter to execute - no trip has been made to the db, and no results have been returned

post = Post.query\
            .join(subquery, Post.id == subquery.c.id)\
            .filter(subquery.c.num_comments > 10)\
            .first() # This is the line that actually executes the query! Here is where we go to the db.

# This results in the following SQL, which makes only one trip to the database:

SELECT *
FROM post JOIN (
    SELECT post.id AS id, count(comment.id) AS num_comments
    FROM post JOIN comment ON comment.post_id = post.id 
    GROUP BY post.id) AS anon_1 ON post.id = anon_1.id
WHERE anon_1.num_comments > 10
LIMIT 1;
```