""" database access
docs:
* http://initd.org/psycopg/docs/
* http://initd.org/psycopg/docs/pool.html
* http://initd.org/psycopg/docs/extras.html#dictionary-like-cursor
"""

from contextlib import contextmanager
import logging
import os

from flask import current_app, g

import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import DictCursor

pool = None

def setup():
    global pool
    DATABASE_URL = os.environ['DATABASE_URL']
    current_app.logger.info(f"creating db connection pool")
    pool = ThreadedConnectionPool(1, 4, dsn=DATABASE_URL, sslmode='require')


@contextmanager
def get_db_connection():
    try:
        connection = pool.getconn()
        yield connection
    finally:
        pool.putconn(connection)


@contextmanager
def get_db_cursor(commit=False):
    with get_db_connection() as connection:
      cursor = connection.cursor(cursor_factory=DictCursor)
      # cursor = connection.cursor()
      try:
          yield cursor
          if commit:
              connection.commit()
      finally:
          cursor.close()

def add_person (name):
    # Since we're using connection pooling, it's not as big of a deal to have
    # lots of short-lived cursors (I think -- worth testing if we ever go big)
    with get_db_cursor(True) as cur:
        current_app.logger.info("Adding person %s", name)
        cur.execute("INSERT INTO person (name) values (%s)", (name,))

def get_people(page = 0, people_per_page = 10):
    ''' note -- result can be used as list of dictionaries'''
    limit = people_per_page
    offset = page*people_per_page
    with get_db_cursor() as cur:
        cur.execute("select * from person order by person_id limit %s offset %s", (limit, offset))
        return cur.fetchall()

def get_gifts_for_person(person):
    with get_db_cursor() as cur:
        cur.execute("select product, external_link from gift_idea where person_id = %s", (person,))
        return cur.fetchall()

def get_name_for_person(person):
    with get_db_cursor() as cur:
        cur.execute("select name from person where person_id = %s", (person,))
        return cur.fetchone()['name']

def get_most_popular_gift():
    with get_db_cursor() as cur:
        cur.execute("select product, external_link from gift_idea group by product, external_link order by count(*) desc;")
        return dict(cur.fetchone())



def get_image(img_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM images where image_id=%s", (img_id,))
        return cur.fetchone()

def upload_image(data, filename):
    with get_db_cursor(True) as cur:
        cur.execute("insert into images (filename, data) values (%s, %s)", (filename, data))

def get_image_ids():
    with get_db_cursor() as cur:
        cur.execute("select image_id from images;")
        return [r['image_id'] for r in cur]
        
        

#################################################
##### LEAVE THIS HERE SO NO ERRORS IN VIEW ######
#################################################






'''
####### EXAMPLE 1
accessing table row as object, object methods
'''

def get_people(page = 0, people_per_page = 10):
    ''' note -- result can be used as list of dictionaries'''
    limit = people_per_page
    offset = page*people_per_page
    with get_db_cursor() as cur:
        cur.execute("select * from person order by person_id limit %s offset %s", (limit, offset))
        return cur.fetchall()

people = get_people()

for person in people:
    print(person['first_name'])
    print(person['first_name'] + ' ' + person['last_name'])


'''
####### EXAMPLE 2
chaining variable number of query parameters, aggregation, etc without defining lots
of custom functions with minute differences
'''

def get_person_by_id(person):
    with get_db_cursor() as cur:
        cur.execute("select * from person where person_id = %s", (person,))
        return cur.fetchone()

def get_person_by_id_and_last_name(person, last_name):
    with get_db_cursor() as cur:
        cur.execute("select * from person where person_id = %s and person_last_name = %s", (person, last_name,))
        return cur.fetchone()

get_person_by_id(1)
get_person_by_id_and_last_name(1, 'Johnson')

def get_people_by_last_name(last_name, asc=True):
    with get_db_cursor() as cur:
        if (asc):
            cur.execute("select * from person where person.last_name = %s order by person.last_name asc", (last_name,))
        else:
            cur.execute("select * from person where person.last_name = %s order by person.last_name desc", (last_name,))
        return cur.fetchone()

get_people_by_last_name('Johnson')
get_people_by_last_name('Johnson', False)


'''
####### EXAMPLE 3
select different columns without defining a different function for each column, for each table
'''
# define a function to get user by username
# define another function to get the birthday of a user
# define another function to get the name of a user


'''
####### EXAMPLE 4
get related entities very easily!
'''

def get_person_by_username(name):
    with get_db_cursor() as cur:
        cur.execute("select id")
        return cur.fetchone()

def get_post_by_author_id(person_id):
    with get_db_cursor() as cur:
        cur.execute("select post.* from post where user.id = %s", (person_id,))
        return cur.fetchone()

def get_comments_by_author_id(person_id):
    with get_db_cursor() as cur:
        cur.execute("select comment.* from comment where user.id = %s", (person_id,))
        return cur.fetchone()

person = get_person_by_username('ted_lasso')
posts = get_post_by_author_id(person['id'])
comments = get_comments_by_author_id(person['id'])