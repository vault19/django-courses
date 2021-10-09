from datetime import timedelta, datetime

from courses.management.notify_cmd import NotifyCommand
from courses.models import Run
from courses.settings import (
    COURSES_NOTIFY_RUN_START_EMAIL_SUBJECT,
    COURSES_NOTIFY_RUN_START_EMAIL_BODY,
    COURSES_NOTIFY_RUN_START_EMAIL_HTML,
)


class Command(NotifyCommand):
    help = "Notify (send email) users that run has started (run start == today +/- time_delta)."
    mail_subject = COURSES_NOTIFY_RUN_START_EMAIL_SUBJECT
    mail_body = COURSES_NOTIFY_RUN_START_EMAIL_BODY
    mail_body_html = COURSES_NOTIFY_RUN_START_EMAIL_HTML

    def handle(self, *args, **options):
        if options["time_delta"]:
            notify_date = datetime.today() + timedelta(days=options["time_delta"])
            notify_date = notify_date.date()
        else:
            notify_date = datetime.today().date()

        runs = Run.objects.filter(start=notify_date)

        if runs.count() > 0:
            if options["verbosity"] >= 2:
                self.stdout.write(f"Found {runs.count()} run(s) starting {notify_date}.")

            for run in runs.all():
                self.notify_users(run, options)
        else:
            self.stdout.write(self.style.SUCCESS("Nothing to do..."))

        super().handle(*args, **options)
