Installation
============

1. Install django-courses via pip::

    pip install django-courses

Alternatively install latest development version from Github::

    pip install https://github.com/vault19/django-courses/archive/refs/heads/main.zip

2. Add "courses" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'courses',
    ]

3. Include the polls URLconf in your project urls.py like this::

    path("", include("courses.urls")),

4. Run `python manage.py migrate` to create the courses tables in DB.

5. Start the development server and visit http://127.0.0.1:8000/admin/
   to manage your courses (you'll need the Admin app enabled).

6. Visit http://127.0.0.1:8000/ to view the courses list.