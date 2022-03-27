## Aggregates

### What is an Aggregate Function in SQL?

An aggregate function in SQL returns one value after calculating multiple values of a column. We often use aggregate functions with the GROUP BY and HAVING clauses of the SELECT statement. The following are the five most common aggregate functions:

![Untitled](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/5dda5321-809b-4c62-afc8-d7a23ffab7c6/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220325%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220325T171645Z&X-Amz-Expires=86400&X-Amz-Signature=7f8d39bb3ccb8b400be507600a2a361d2c1158594592ac79e2fdbf526599536b&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22Untitled.png%22&x-id=GetObject)
This is how the SQL statements would look.
```sql
SELECT MIN(id)
FROM Comments;

SELECT MAX(id)
FROM Comments;

SELECT SUM(id)
FROM Comments;

SELECT AVG(id)
FROM Comments;

SELECT COUNT(id)
FROM Comments;

```
This is how those functions are translated into flask-sqlalchemy.
```python
MIN()
db.func.min()

MAX()
db.func.max()

SUM()
db.func.sum([COLUMN]) - Adds the numerical values in a column

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

```python
db.session.query(func.count(User.first_name).group_by(User.first_name).all()
```

## Joins

The effect of joining is achieved by just placing two tables in either the columns clause or the where clause of the select() construct. Now we use the join() and outerjoin() methods. 

The `join()` method returns a join object from one table object to another. 

```python
join(right, onclause = None, isouter = False, full = False)
```

The functions of the parameters mentioned in the above code are as follows - 

- **right** - the right side of the join; this is any table object
- **onclause** - a SQL expression representing the ON clause of the join. If left at None, it attempts to join the two tables based on a foreign key relationship.
- **isouter** − if True, renders a LEFT OUTER JOIN, instead of JOIN
- **full** − if True, renders a FULL OUTER JOIN, instead of LEFT OUTER JOIN

Alright let’s look at two tables, the Post table and the comment table. We can construct a simple implicit join between Post and Comment, we can use Query.filter() to equate their related columns toegther. 

something like..

```python
r = db.session.query(Post, Comment).join(Comment, Comment.post_id == Post.id).all()
```

This should return a result of a list of tuples (Post object, Comment object) and we can iterate through them using a for loop andextract any information that I need. 

```python
for post, comment in r:
  print(post.title, comment.body)
```

And the SQL expression would look something like:

```sql
SELECT Post.id

FROM Post JOIN Comment

ON Post.id = Comment.post_id
```

We perform our JOIN using the join() method. The first parameter we pass is the data model we’ll be joining with on the “right.” We then specify what we’ll be joining with “on”: the post_id column of our Comment model, and the id column of our Post model.

In addition to simple JOINs, we can perform outer JOINs, which is essentially just a left join using the following syntax:

```python
r = db.session.query(Post, Comment).outerjoin(Comment, Comment.post_id == Post.id).all()
```
This would result in a list of tuples. The first part of the tuple would be a post and the second part would be a comment. 


```python[(<Post 1>, <Comment 10>), (<Post 1>, <Comment 18>), (<Post 2>, <Comment 3>), (<Post 3>, None)]
```

If we wanted to loop over these results we can do it by

```python
for result in r:
	print('POST: {} COMMENT POSTED: {}'.format(result[0].title, result[1].body)
```

Now what we will notice is that we *may* get an error saying that AttributeError: ‘NoneType’ object has no attribute ‘body’. And the reason for this is because well, if we look back at our list of tuples. We notice that some Posts are associated with no comments, and have None listed as the second thing in the tuple. This is because, well, not all posts have comments. In order for us to get rid of this error we can add an if condition to our for loop before printing the post and the comment

```python
for result in r:
	if result[1]:
		print('POST: {} COMMENT POSTED: {}'.format(result[0].title, result[1].body)
```

The SQL equivalent to the query would be

```sql
SELECT *
FROM Post LEFT JOIN Comment
ON Post.id == Comment.post_id;
```

If we wanted to we could have also just get the post title and comment body directly instead of referencing the class and getting an object back in our tuple

```python
r = db.session.query(Post.title, Comment.body).outerjoin(Comment, Comment.post_id == Post.id).all()
```

Doing a left join is pretty easy, you just have to remember to use the `outerjoin`, mention the table you want to join to and the joint condition.

