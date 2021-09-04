from django.conf import settings

EXTENSION_IMAGE = ['jpg', 'jpeg', 'gif', 'png', 'tiff', 'svg']
EXTENSION_DOCUMENT = ['pdf',]
EXTENSION_VIDEO = ['mkv', 'avi', 'mp4', 'mov']

MAX_FILE_SIZE_UPLOAD = getattr(settings, 'MAX_FILE_SIZE_UPLOAD', 50)
MAX_FILE_SIZE_UPLOAD_FRONTEND = getattr(settings, 'MAX_FILE_SIZE_UPLOAD_FRONTEND', 2)

# Default redirect from index page
COURSES_LANDING_PAGE_URL = getattr(settings, 'COURSES_LANDING_PAGE_URL', 'all_active_runs')

# Wheather to dispaly link to chapter detail page (page will still be accessible, but it might be too much views)
COURSES_DISPLAY_CHAPTER_DETAILS = getattr(settings, 'COURSES_DISPLAY_CHAPTER_DETAILS', True)

# Whether to allow submission for the whole chapter.
COURSES_ALLOW_SUBMISSION_TO_CHAPTERS = getattr(settings, 'COURSES_ALLOW_SUBMISSION_TO_CHAPTERS', True)
# Whether to allow submission for specific lecture.
COURSES_ALLOW_SUBMISSION_TO_LECTURES = getattr(settings, 'COURSES_ALLOW_SUBMISSION_TO_LECTURES', True)

# In run details display also future chapters that are not available yet.
COURSES_SHOW_FUTURE_CHAPTERS = getattr(settings, 'COURSES_SHOW_FUTURE_CHAPTERS', False)

# Wheather to show 404 or the details of the chapter if it has passed.
COURSES_ALLOW_ACCESS_TO_PASSED_CHAPTERS = getattr(settings, 'COURSES_ALLOW_ACCESS_TO_PASSED_CHAPTERS', True)
# Wheather to show 404 or the details of the chapter if it has passed.
COURSES_ALLOW_SUBMISSION_TO_PASSED_CHAPTERS = getattr(settings, 'COURSES_ALLOW_SUBMISSION_TO_PASSED_CHAPTERS', False)
