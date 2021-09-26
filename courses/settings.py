from django.conf import settings

EXTENSION_IMAGE = ["jpg", "jpeg", "gif", "png", "tiff", "svg"]
EXTENSION_DOCUMENT = ["pdf"]
EXTENSION_VIDEO = ["mkv", "avi", "mp4", "mov"]

MAX_FILE_SIZE_UPLOAD = getattr(settings, "MAX_FILE_SIZE_UPLOAD", 50)
MAX_FILE_SIZE_UPLOAD_FRONTEND = getattr(settings, "MAX_FILE_SIZE_UPLOAD_FRONTEND", 2)

# Default redirect from index page
COURSES_LANDING_PAGE_URL = getattr(settings, "COURSES_LANDING_PAGE_URL", "all_active_runs")

# Wheather to dispaly link to chapter detail page (page will still be accessible, but it might be too much views)
COURSES_DISPLAY_CHAPTER_DETAILS = getattr(settings, "COURSES_DISPLAY_CHAPTER_DETAILS", True)

# Wheather allow users to subscribe to run that has already started.
COURSES_ALLOW_SUBSCRIPTION_TO_RUNNING_COURSE = getattr(settings, "COURSES_ALLOW_SUBSCRIPTION_TO_RUNNING_COURSE", True)
# Wheather allow users to unsubscribe from any course run.
COURSES_ALLOW_USER_UNSUBSCRIBE = getattr(settings, "COURSES_ALLOW_USER_UNSUBSCRIBE", True)

# Whether to allow submission for the whole chapter.
COURSES_ALLOW_SUBMISSION_TO_CHAPTERS = getattr(settings, "COURSES_ALLOW_SUBMISSION_TO_CHAPTERS", True)
# Whether to allow submission for specific lecture.
COURSES_ALLOW_SUBMISSION_TO_LECTURES = getattr(settings, "COURSES_ALLOW_SUBMISSION_TO_LECTURES", True)

# In run details display also future chapters that are not available yet.
COURSES_SHOW_FUTURE_CHAPTERS = getattr(settings, "COURSES_SHOW_FUTURE_CHAPTERS", False)

# Wheather to show 404 or the details of the chapter if it has passed.
COURSES_ALLOW_ACCESS_TO_PASSED_CHAPTERS = getattr(settings, "COURSES_ALLOW_ACCESS_TO_PASSED_CHAPTERS", True)
# Wheather to show 404 or the details of the chapter if it has passed.
COURSES_ALLOW_SUBMISSION_TO_PASSED_CHAPTERS = getattr(settings, "COURSES_ALLOW_SUBMISSION_TO_PASSED_CHAPTERS", False)

# Email settings
COURSES_EMAIL_SUBJECT_PREFIX = getattr(settings, "COURSES_EMAIL_SUBJECT_PREFIX", "")
COURSES_SUBSCRIBED_EMAIL_SUBJECT = getattr(
    settings, "COURSES_SUBSCRIBED_EMAIL_SUBJECT", "courses/emails/subscribed_email_subject.txt"
)
COURSES_SUBSCRIBED_EMAIL_BODY = getattr(
    settings, "COURSES_SUBSCRIBED_EMAIL_BODY", "courses/emails/subscribed_email_body.txt"
)
COURSES_SUBSCRIBED_EMAIL_HTML = getattr(
    settings, "COURSES_SUBSCRIBED_EMAIL_HTML", "courses/emails/subscribed_email_body.html"
)

COURSES_NOTIFY_RUN_START_EMAIL_SUBJECT = getattr(
    settings, "COURSES_NOTIFY_RUN_START_EMAIL_SUBJECT", "courses/emails/run_start_email_subject.txt"
)
COURSES_NOTIFY_RUN_START_EMAIL_BODY = getattr(
    settings, "COURSES_NOTIFY_RUN_START_EMAIL_BODY", "courses/emails/run_start_email_body.txt"
)
COURSES_NOTIFY_RUN_START_EMAIL_HTML = getattr(
    settings, "COURSES_NOTIFY_RUN_START_EMAIL_HTML", "courses/emails/run_start_email_body.html"
)
