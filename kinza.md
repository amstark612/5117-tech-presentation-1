## Aggregates

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/5dda5321-809b-4c62-afc8-d7a23ffab7c6/Untitled.png)

```jsx
MIN()
db.func.min()

MAX()
db.func.max()

SUM()
db,func.sum([COLUMN]) - Adds the numerical values in a column

AVG()
db.func.avg()

COUNT()
db.func.count([COLUMN]) - counts the number of records in a column

db.func.count(distinct([COLUMN])) - counts the distinct number of records in a column

//count the number of records with a 'first_name' value
db.session.query(func.count(User.first_name).all()

//count the number of DISTINCT 'first_name' values
db.session.query(func.count(distinct(User.first_name)).all()
```

Of course, we can use the group_by() method on queries based on aggregates as well. group_by() works similarly to what we’d expect from SQL:

db.session.query(func.count(User.first_name).group_by(User.first_name).all()

## Joins

The effect of joining is achieved by just placing two tables in either the columns clause or the where clause of the select() construct. Now we use the join() and outerjoin() methods. 

The join() method returns a join object from one table object to another. 

join(right, onclause = None, isouter = False, full = False)

The functions of the parameters mentioned in the above code are as follows - 

- **right** - the right side of the join; this is any table object
- **onclause** - a SQL expression representing the ON clause of the join. If left at None, it attempts to join the two tables based on a foreign key relationship.
- **isouter** − if True, renders a LEFT OUTER JOIN, instead of JOIN
- **full** − if True, renders a FULL OUTER JOIN, instead of LEFT OUTER JOIN

Alright let’s look at two tables, the Post table and the comment table. We can construct a simple implicit join between Post and COment, we can use Query.filter() to equate their related columns toegther. 

something like..

`db.session.query(Post).join(Comment, Comment.post_id == Post.id).all()`

And the SQL expression would look something like:

`SELECT [Post.id](http://Post.id)`

`FROM Post JOIN Comment`

`WHERE [Post.id](http://Post.id) = Comment.post_id`

We perform our JOIN using the join() method. The first parameter we pass is the data model we’ll be joining with on the “right.” We then specify what we’ll be joining with “on”: the post_id column of our Comment model, and the id column of our Post model.

In addition to simple JOINs, we can perform outer JOINs using the same syntax:

`db.session.query(Post).join(Comment, Comment.post_id == Post.id).all()`
