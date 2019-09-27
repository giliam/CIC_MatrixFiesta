# CIC MatrixFiesta

[![Build Status](https://travis-ci.org/giliam/CIC_MatrixFiesta.svg?branch=master)](https://travis-ci.org/giliam/CIC_MatrixFiesta) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/046108c026134cbeb180e2f162837dde)](https://www.codacy.com/manual/giliam/CIC_MatrixFiesta?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=giliam/CIC_MatrixFiesta&amp;utm_campaign=Badge_Grade)

Website designed so students can evaluate themselves on the different parts of the program. Teachers can also provide an evaluation or validate students'.

## How to
Uses **Python 3** and **Django** `>=2.2.4`.

Fill a `parameters.py` file into *matrix_fiesta* folder containing `TEMPLATES_DIRS` and `STATIC_ROOT` values. You can also specify `DATABASES` configuration if you don't want to use *sqlite3*.

Compile messages for a *french version* of the text 

> `python manage.py compilemessages`

and migrate the database 

> `python manage.py migrate`

You can also load sample data from *matrix_fiesta/fixtures/* folder

> `python manage.py loaddata matrix/fixtures/*.json`

You can then run the server

> `python manage.py runserver`

A superuser exists with **admin** login and **matrix_fiesta** password. All other users have the same password.
