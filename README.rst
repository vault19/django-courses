=======
Courses
=======

.. image:: https://img.shields.io/pypi/pyversions/django-courses.svg
   :target: https://pypi.org/project/django-courses/

.. image:: https://img.shields.io/github/license/vault19/django-courses.svg
   :target: https://github.com/vault19/django-courses/blob/master/LICENSE

Courses is a simple Django app to manage online courses (education). Appliaction is already used by civic association
`SPy o.z. <https://python.sk/o_nas/>`_ (non-profit) for project "Teaching with hardware" in Slovak "Učíme s hardvérom":
https://kurzy.ucimesharverom.sk

Project "Učíme s hárverom" is run in Slovak language (how ever this app is in English, but has Slovak translations)
and is aimed for Slovak teachers to introduce hardware (such as `BBC microbit <https://microbit.org/>`_) into computing
lessons at primary and secondary schools.

Quick start
-----------

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

Testing
-------

App is using Django's build in test framework. However, there are only a few tests :(

In order to run tests execute command (in your project)::

     python manage.py test

Support
-------

`Vault19 o.z. <https://vault19.eu>`_ (non profit micro hackerspace) did this app because
`SPy o.z. <https://python.sk/o_nas/>`_ (non profit supporting Slovak Python community) needed something for better
management of their courses. We like to program and we wanted to design a clean
`Django <https://www.djangoproject.com/>`_ app and learn one or two things in the process...