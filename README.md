$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt

Set up the database:

(venv) $ psql
=# CREATE DATABASE warbler;
=# (control-d)
(venv) $ python seed.py

to run - flask run -p 3001