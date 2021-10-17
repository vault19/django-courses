Contributors Guide
==================

We are happy with any volunteers involvement in `django-courses <https://github.com/vault19/django-courses>`_ app. If you would like to help us, there are multiple ways to do so. Depending on your skills and type of work you would like to do (doesn’t have to be development), we encourage you to start with any of the following:

Write a blog, get involved on social media or make a talk
---------------------------------------------------------

You can help out by spreading the word about `django-courses <https://github.com/vault19/django-courses>`_. Or may be about the project that has started it: https://ucimeshardverom.sk if you were participant of the past courses...

Update documentation
--------------------

Good documentation is key. How ever this projct lacks a good documentation and we need to change that! If you don't know how to do something, we probably missed to wrote it down. Documentation is a never ending process so we welcome any improvement suggestions, feel free to create issues in our bug tracker.

If you feel that our documentation needs to be modified or we missed something, feel free to submit PR or create and issue on `Github <https://github.com/vault19/django-courses/issues/>`_.

Suggest an improvement or report bug
------------------------------------

All issues are handled by `GitHub issue tracker <https://github.com/vault19/django-courses/issues>`_, if you've found a bug please create an issue for it.

If there is something you are missing, and wish to be implemented in `django-courses <https://github.com/vault19/django-courses>`_, feel free to create an issue and mark it as an enhancement.

Update django-courses
---------------------

All development is done on `GitHub <https://github.com/vault19/django-courses>`_. If you decide to work on existing issue, **please mention in the issue comment that you are working on it so other people do not work on the same issue**. Create your `fork <https://github.com/vault19/django-courses/fork>`_ and **in new branch update code**. Once you are happy with your changes create `pull request <https://help.github.com/articles/using-pull-requests>`_ and we will review and merge it as soon as we can. To make the life easier please do all your work in a `separate branch <https://git-scm.com/book/en/v1/Git-Branching>`_ (if there are multiple commits we do `squash merge <https://github.com/blog/2141-squash-your-commits>`_), if there is a issue for your change should include the issue number in the branch name and merge request description so they are linked on GitHub. We encourage you to write tests for your code. Once you request merge request on GitHub, there will be an automated test run, please make sure each test passes. Sometimes it take few minutes for the Github actions to start tests, so please be patient. We encourage you to do the best practice and write the tests, but event if you don't we will accept the pull request.

Write a test
------------

We realize that there is never too much testing, so you can help us by creating any form of automated testing. You will improve our continuous integration and make the project harder to break.

Translate app
-------------

App can be localized to different languages. We have included only Slovak language so far, if you know any foreign language add a translation.

Getting help
------------

If you look for help, visit our monthly meetups in Bratislava.

Developer's HowTo
=================

Development standards
---------------------

* We do use standard PEP8, with extended line to 120 characters.
* We do format the code with Black formatter.
* Each pull request is tested against our automated test suite (yes, PEP8 and Black are part of the tests).
* Writing automated tests for the new code is preferred, but not required. How to write a test read more below in testing metodology.

Development setup
-----------------

This is reusable django app, which means you have to create project first. If you dont know what that means, or what is the difference we suggest you go through Django tutorial first. It is great resource to understand Django better.

Create directory and run the following commands (in Linux, or Mac).

1. ``python3 -m venv envs3`` this will create virtual environments for you, where you can install all requirements needed
2. ``source envs3/bin/activate`` activate virtual environments
3. ``pip install django`` install out main dependency
4. ``django-admin startproject website`` start your own django project (feel free to name it differently than website)
5. ``git clone git@github.com:YOUR-GITHUB-ACCOUNT/django-courses.git`` make a clone of your fork of django-courses
6. ``cd website`` lets go inside the project directory
7. ``ln -s ../django-courses/courses .`` create a symbolic link to it is in PYTHONPATH and app can be found by Django
8. in website/settings.py add ``courses`` into INSTALLED APPS
9. ``path("", include("courses.urls")),`` include courses urls in project's website/urls.py file (don't forget from django.conf.ulrs import include)
10. ``python manage.py migrate`` execute migration so it will pre-populate the DB structure
11. ``python manage.py loaddata courses/fixtures/test_data.json`` insert dummy data into DB
12. ``python manage.py runserver`` start development server, and check the app in browser

Development methodology
-----------------------

1. You create a `fork <https://github.com/vault19/django-courses/fork>`_ of the project (you do this only once. Afterwards you already have it in your GitHub, it is your repo in which you are doing all the development).
2. Clone your fork locally ``git clone git@github.com:YOUR-GITHUB-ACCOUNT/django-courses.git`` add upstream remote to be able to download updated into your fork ``git remote add upstream https://github.com/vault19/django-courses.git``. You don't have the right to push to upstream, but do regularly pull and push to your fork to keep it up-to-date and prevent conflicts.
3. Pick up a `issue <https://github.com/vault19/django-courses/issues>`_, and make a comment that you are working on it.
4. In your local git copy you create a branch: ``git checkout -b XX-new-feature`` (where XX is issue number).
5. Coding time:

   * Do commit how often you need. At this point doesn't matter if code is broken between commits.
   * Store your change in your repo at GitHub. You can push to server how many times you want: ``git push origin XX-new-feature``.
   * Merge the code from upstream as often as you can: ``git pull upstream master``. At this point we don't care about merge message, or rebase to get rid of it. We will do `squash merge <https://github.com/blog/2141-squash-your-commits>`_ (in upstream master it will looks like one commit).
   * Anytime during development execute ``python manage.py test courses`` to run all tests, make sure all passes before creating PR.

6. Once you are happy with your code, you click on `pull request <https://help.github.com/articles/using-pull-requests>`_ button, and select master branch in upstream and XX-new-feature branch from your repo. At this point automated tests will be run if everything is OK, if you see some errors please fix them and push your fix into your branch. This way the pull request is updated with fixes and tests are run again.
7. In case reviewer asks for changes you can do all the things mentioned in point 5. Once happy with the changes make a note in pull request to review again.
8. Your feature is approved and merged to master of upstream, so you can check out master at your local copy: ``git checkout master`` and pull the newly approved changes from upstream ``git pull upstream master``. Pull from upstream will download your work (as one commit into master) that has been done in branch. Now you can delete your local branch ``git branch --delete XX-new-feature``, and also remote one ``git push origin :XX-new-feature``.

Testing setup
-------------

In order to run app's tests you need to execute command (in your project)::

     python manage.py test courses

Testing metodology
------------------

App is using Django's build in test framework. However, there are only a few tests :(

Feel free to write any test in Django's build in framework (Selenium tests are welcomed as well).