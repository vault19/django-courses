Settings
========

A django-courses settings file contains all the configuration of your application. This document explains how settings work and which settings are available.

The basics
----------

A settings file is just a Python module with module-level variables. Because a settings file is a Python module, the following apply:

* It doesn’t allow for Python syntax errors.
* It can assign settings dynamically using normal Python syntax.
* It can import values from other settings files.
* Django project settings can overwrite values defined in django-courses settings defaults.

Core Settings
=============

Here’s a list of settings available in django-courses and their default values.

EXTENSION_IMAGE
---------------

Default: **["jpg", "jpeg", "gif", "png", "tiff", "svg"]**


EXTENSION_DOCUMENT
------------------

Default: **["pdf"]**

EXTENSION_VIDEO
---------------

Default: **["mkv", "avi", "mp4", "mov"]**

MAX_FILE_SIZE_UPLOAD
--------------------

Default: **50**

MAX_FILE_SIZE_UPLOAD_FRONTEND
-----------------------------

Default: **2**

COURSES_LANDING_PAGE_URL
------------------------

Default: **"all_active_runs"**

Default redirect from index page.

COURSES_LANDING_PAGE_URL_AUTHORIZED
-----------------------------------

Default: **"all_subscribed_active_runs"**

Default redirect from index page for users that are already logged in.

COURSES_DISPLAY_CHAPTER_DETAILS
-------------------------------

Default: **True**

Wheather to dispaly link to chapter detail page (page will still be accessible, but it might be too much views)

COURSES_ALLOW_SUBSCRIPTION_TO_RUNNING_COURSE
--------------------------------------------

Default: **True**

Wheather allow users to subscribe to run that has already started.

COURSES_ALLOW_USER_UNSUBSCRIBE
------------------------------

Default: **True**

Wheather allow users to unsubscribe from any course run.

COURSES_ALLOW_SUBMISSION_TO_CHAPTERS
------------------------------------

Default: **True**

Whether to allow submission for the whole chapter.

COURSES_ALLOW_SUBMISSION_TO_LECTURES
------------------------------------

Default: **True**

Whether to allow submission for specific lecture.

COURSES_SHOW_FUTURE_CHAPTERS
----------------------------

Default: **False**

In run details display also future chapters that are not available yet.

COURSES_ALLOW_ACCESS_TO_PASSED_CHAPTERS
---------------------------------------

Default: **True**

Wheather to show 404 or the details of the chapter if it has passed.

COURSES_ALLOW_SUBMISSION_TO_PASSED_CHAPTERS
-------------------------------------------

Default: **False**

Wheather to show 404 or the details of the chapter if it has passed.

# Email settings
COURSES_EMAIL_SUBJECT_PREFIX
----------------------------

Default: **""**

Default prefix in all emails. Value is prepended to each email subject setting below.

COURSES_SUBSCRIBED_EMAIL_SUBJECT
--------------------------------

Default: **"courses/emails/subscribed_email_subject.txt"**

COURSES_SUBSCRIBED_EMAIL_BODY
-----------------------------

Default: **"courses/emails/subscribed_email_body.txt"**

COURSES_SUBSCRIBED_EMAIL_HTML
-----------------------------

Default: **"courses/emails/subscribed_email_body.html"**

File does not exists within project. If file does not exists just plain text email is send. If specified to existing file html will be send as an rich mail with text version.

COURSES_NOTIFY_RUN_START_EMAIL_SUBJECT
--------------------------------------

Default: **"courses/emails/run_start_email_subject.txt"**

COURSES_NOTIFY_RUN_START_EMAIL_BODY
-----------------------------------

Default: **"courses/emails/run_start_email_body.txt"**

COURSES_NOTIFY_RUN_START_EMAIL_HTML
-----------------------------------

Default: **"courses/emails/run_start_email_body.html"**

File does not exists within project. If file does not exists just plain text email is send. If specified to existing file html will be send as an rich mail with text version.

COURSES_NOTIFY_CHAPTER_OPEN_EMAIL_SUBJECT
-----------------------------------------

Default: **"courses/emails/chapter_open_email_subject.txt"**

COURSES_NOTIFY_CHAPTER_OPEN_EMAIL_BODY
--------------------------------------

Default: **"courses/emails/chapter_open_email_body.txt"**

COURSES_NOTIFY_CHAPTER_OPEN_EMAIL_HTML
--------------------------------------

Default: **"courses/emails/chapter_open_email_body.html"**

File does not exists within project. If file does not exists just plain text email is send. If specified to existing file html will be send as an rich mail with text version.

COURSES_NOTIFY_MEETING_START_EMAIL_SUBJECT
------------------------------------------

Default: **"courses/emails/meeting_start_email_subject.txt"**

COURSES_NOTIFY_MEETING_START_EMAIL_BODY
---------------------------------------

Default: **"courses/emails/meeting_start_email_body.txt"**

COURSES_NOTIFY_MEETING_START_EMAIL_HTML
---------------------------------------

Default: **"courses/emails/meeting_start_email_body.html"**

File does not exists within project. If file does not exists just plain text email is send. If specified to existing file html will be send as an rich mail with text version.