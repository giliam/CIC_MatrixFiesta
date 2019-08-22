# CIC MatrixFiesta

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
