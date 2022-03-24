# The main Structure of this part of the presentation

* Insert

* Update

* Filter

## Insert

The Insert action consist of 6 sub-tasks, they are:

* object constructed
* adding
* flushing
* autogenerate primary key (optional)
* map(optional)
* commit

1. ### Constructing the object

    When using the ORM, the `Session` object is responsbile for constructing `Insert` constructs and emitting them for us in a transaction. We add the object entry to the `Session`, then the `Session` will make sure new change will be emitted to the database when they are needed, using a process known as a `flush`

    Let's say we have a class session named `User`, it contains `id`, `username`, `display_name`, `first_name`, `last_name` and `birthday`

    ~~~python
    class User(db.Model):
        id = db.Column(db.Text, primary_key=True, nullable=False)
        username = db.Column(db.String(30), unique=True, nullable=False)
        display_name = db.Column(db.String(30))
        first_name = db.Column(db.String(30), nullable=False)
        last_name = db.Column(db.String(30), nullable=False)
        birthday = db.Column(db.Date)
    ~~~

    If we use ORM technique to insert a new entry, the code can simply by

    ~~~~sql
    User1 = User(id = `1`, username = `username1`, display_name = `display_name1`, first_name = `first`, last_name = `last`, birthday = `1997-02-09`)
    ~~~~

    What we have done above is constructing an object using the names of the mapped columns as keyword arguments.
    So when we type

    ~~~~sql
    User1
    ~~~~

    it will return
    >User(id = `1`, username = `username1`, display_name = `display_name1`, first_name = `first`, last_name = `last`, birthday = `1997-02-09`)

    **** could add here that what is returned is an object with properties, so we could call `User1.display_name` and it would return `display_name1`, etc ****

    ORM on SQLAlchemy integrate with auto-increment primary key feature, thus based on your choice, you can choose not have the `id` in your object set up. We will talk about it later

2. ### Adding objects to a Session

    **** it is counterintuitive to call a session something like `User` because any type of object can be added to a session, you can think of a session as something more general, like when you `psql` in your console, that is opening a session for example, so maybe `session.add()` is more intuitive ****

    We have constructed a session named `User`, then we can use method `.add()` method to add the `object` to the `User` session

    ~~~~sql
    User.add(User1)
    ~~~~

    > if we use normal SQL commend, the code may look like this
    >
    > ~~~~sql
    > INSERT INTO User
    > VALUES (`1`, `username1`, `display_name1`, `first`, `last`, `1997-02-09`)  
    > ~~~~

3. ### Flushing

    The Session will accumulates changes on at a time, but it will not communicate them to the database until needed. This allows it to make better decisions about how SQL DML should be emitted in the transaction based on a given set of pending changes. When it does emit SQL to the database to push the currect set of change, the `flush` is needed.

    ~~~~sql
    User1.flush() 
    ~~~~

    > if we use normal SQL commend, the code may look like this
    >
    > ~~~~sql
    >BEGIN (implicit)
    >INSERT INTO User (username, display_name) VALUES (?, ?)
    >[...] ('username1', 'display_name1')
    >INSERT INTO User (username, display_name) VALUES (?, ?)
    >[...] ('Yizhe Wang', 'Peter')
    > ~~~~

    When the `session` was first created, it also create a new transaction, it will remians open until we call `commit()` method on it.
    >Import Notes: The Session feature has `autoflush` feature, thus we only use `flush()` when we want to manually update changes

4. ### Autogenerated primary key

    Once the entry is inserted, the object we created are in a state known as `persistent`, they are associated with the `User`
    And when the `INSERT` is done, ORM will reterived the new primary key identifiers for each new object.

    ~~~~sql
    # creating an object without the primary key
    User2 = User(username = `username2`, display_name = `display_name2`, first_name = `first2`, last_name = `last2`, birthday = `1997-01-03`)
    # add second user
    User.add(User2)
    ~~~~

    ~~~~sql
    User2.id
    ~~~~

    > The commend above will return `2`

5. ### Commit

    At the end, we can `commit` our change to the database by running the `.commit()` method.

    ~~~~sql
    User1.commit()
    ~~~~

## Update

When using the ORM, there are two ways to update ORM objects.

* The primary way is that it is emitted automaticlly as part of the `unit of work` processed by the `Session` where an `UPDATE` action is emitted on a per-primary key basis coressponding to individual objects that have changes on them

    > `Unit of work` : the system transparently keeps track of changes to objects and periodically flushes all those pending > changes out to the database

* The second form of `UPDATE` allows you to use the `Update` consturct with the `Session` explicitly.

We will mainly focus on the first approach

The Insert action consist of 6 sub-tasks, they are:

* retrive information
* update

1. ### retrive information

    We can use `.get()`, `.query.filter()` or `query.filter_by()` to retrive the information from the database

    `.get()` is used when you know the primary key for sure

    ~~~~sql
    object1 = User.get(id='1').first()
    ~~~~

    > `.first()` Return the first result of this Query or None if the result doesn’t contain any row.

    ~~~~sql
    object1
    # will print
    # User(id = `1`, username = `username1`, display_name = `display_name1`, first_name = `first`, last_name = `last`, birthday = `1997-02-09`)
    ~~~~

     ***we will discuss the `filter()` and `filter_by()` in the next chapter***

2. ### update

    If we want to update the `username` from `username1` to `Peter`
    >User1.username = 'Peter'

    Then the object will appears in a collection called Session.dirty(`User.dirty`) indicate the object is dirty
    >User1 in User.dirty -> True

    Then when we ready to commit a change, the `autoflush` will occur, the `Update` was officially emitted.
    then
    >User1 in User.dirty -> False

    ~~~~sql
    object1 = User.get(id='1').first()
    # will print
    # User(id = `1`, username = `Peter`, display_name = `display_name1`, first_name = `first`, last_name = `last`, birthday = `1997-02-09`)
    ~~~~

### Filter

When using the filter feature in the SQLAlchemy, generally speaking, there are two methods, they are:

* Session.query.filter(*criterion)

* Session.query.filter_by(**kwargs)

The main difference is, `filter_by` is used for simple queries on the column names using regular kwargs, the same can be acomplised with `filter`, not using kwargs, but instead using pythonic filtering arguments like `==` equality operator.

~~~~sql

# create session

class User(db.Model):
        id = db.Column(db.Text, primary_key=True, nullable=False)
        username = db.Column(db.String(30), unique=True, nullable=False)
        display_name = db.Column(db.String(30))
        first_name = db.Column(db.String(30), nullable=False)
        last_name = db.Column(db.String(30), nullable=False)
        birthday = db.Column(db.Date)

# create multiple objects
User1 = User(id = `1`, username = `username1`, display_name = `display_name1`, first_name = `first_1`, last_name = `last_1`, birthday = `1997-02-09`)

User2 = User(id = `2`, username = `username2`, display_name = `display_name2`, first_name = `first_2`, last_name = `last_2`, birthday = `1997-02-09`)

User3 = User(id = `3`, username = `username2`, display_name = `display_name3`, first_name = `first_3`, last_name = `last_3`, birthday = `1997-02-09`)

# add objects
User.add(User1)
User.add(User2)
User.add(User3)
~~~~

1. ### filter(*criterion)

    Applying the given filtering criterion to a copy of tihs Query, using SQL expressions.

    Example using the `User` session:

    ~~~~sql
    # single criteria
    object1 = User.query.filter(User.name == 'username1').first()

    # multiple criteria
    object1 = User.query.filter(User.name == 'username1', User.birthday = `1997-02-09`).first()
    ~~~~

2. ### filter_by(**kwargs)

    Apply the given filtering criterion to a copy of this Query, using keyword expression

    Example using the `User` session:

    **** don't forget to update these to `filter_by`! :) ****
    ~~~~sql
    # single criteria
    object1 = User.query.filter(name = 'username1').first()

    # multiple criteria
    object1 = User.query.filter(name = 'username1', birthday = `1997-02-09`).first()
    ~~~~