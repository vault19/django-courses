from datetime import timedelta, datetime

from courses.management.notify_cmd import NotifyCommand
from courses.models import Meeting
from courses.settings import (
    COURSES_NOTIFY_MEETING_START_EMAIL_SUBJECT,
    COURSES_NOTIFY_MEETING_START_EMAIL_BODY,
    COURSES_NOTIFY_MEETING_START_EMAIL_HTML,
)


class Command(NotifyCommand):
    help = "Notify (send email) users that meeting will start (meeting start == today +/- time_delta)."
    mail_subject = COURSES_NOTIFY_MEETING_START_EMAIL_SUBJECT
    mail_body = COURSES_NOTIFY_MEETING_START_EMAIL_BODY
    mail_body_html = COURSES_NOTIFY_MEETING_START_EMAIL_HTML

    def handle(self, *args, **options):
        if options["time_delta"]:
            notify_date = datetime.today() + timedelta(days=options["time_delta"])
            notify_date = notify_date.date()
        else:
            notify_date = datetime.today().date()

        meetings = Meeting.objects.filter(start__date=notify_date)

        if meetings.count() > 0:
            if options["verbosity"] >= 2:
                self.stdout.write(f"Found {meetings.count()} meeting(s).")

            for meeting in meetings.all():
                counter = 0

                if options["verbosity"] >= 1:
                    self.stdout.write(f"{meeting}: starts {meeting.start}.")

                counter += 1
                self.mail_template_variables["meeting"] = meeting

                if options["verbosity"] >= 2:
                    self.stdout.write("Organizer: ", ending="")
                    self.stdout.write(self.style.WARNING(meeting.organizer))

                if meeting.organizer.email and meeting.organizer.email != meeting.run.manager.email:
                    self.send_email(
                        meeting.organizer,
                        meeting.run,
                        verbosity=options["verbosity"],
                        delay=options["delay"],
                        confirm=options["confirm"],
                    )

                if options["verbosity"] >= 2:
                    self.stdout.write("Leader: ", ending="")
                    self.stdout.write(self.style.WARNING(meeting.organizer))

                if meeting.leader and meeting.leader.email and \
                        meeting.leader.email != meeting.run.manager.email:
                    self.send_email(
                        meeting.leader,
                        meeting.run,
                        verbosity=options["verbosity"],
                        delay=options["delay"],
                        confirm=options["confirm"],
                    )

                self.notify_users(meeting.run, options)

        else:
            self.stdout.write(self.style.SUCCESS("Nothing to do..."))

