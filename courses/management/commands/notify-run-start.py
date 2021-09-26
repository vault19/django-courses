from datetime import timedelta, datetime
from time import sleep

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string

from courses.models import Run
from courses.settings import (
    COURSES_EMAIL_SUBJECT_PREFIX,
    COURSES_NOTIFY_RUN_START_EMAIL_SUBJECT,
    COURSES_NOTIFY_RUN_START_EMAIL_BODY,
    COURSES_NOTIFY_RUN_START_EMAIL_HTML,
)


class Command(BaseCommand):
    help = "Notify users that run will start soon."

    def add_arguments(self, parser):
        parser.add_argument(
            "--time-delta", type=int, help="Time delta (in days) for run start comparasion adjustments."
        )
        parser.add_argument(
            "--delay", nargs="?", type=int, help="Time delay (in seconds) between each email.", default=0
        )
        parser.add_argument("--confirm", action="store_true", help="Confirm user prompt to send out emails.")

    def notify(self, user, run, verbosity=1, delay=0, confirm=False):
        if not confirm:
            self.stdout.write(f"Do you really want to send notification email to: {user} ?")
            user_input = input()

            if user_input.lower() != "y":
                self.stdout.write(self.style.WARNING("Confirmation failed! No email is send..."))
                return

        ctx_dict = {
            "user": user,
            "course_run": run,
        }
        subject = COURSES_EMAIL_SUBJECT_PREFIX + render_to_string(COURSES_NOTIFY_RUN_START_EMAIL_SUBJECT, ctx_dict)
        # Email subject *must not* contain newlines
        subject = "".join(subject.splitlines())
        message = render_to_string(COURSES_NOTIFY_RUN_START_EMAIL_BODY, ctx_dict)

        email_message = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

        if COURSES_NOTIFY_RUN_START_EMAIL_HTML:
            try:
                message_html = render_to_string(COURSES_NOTIFY_RUN_START_EMAIL_HTML, ctx_dict)
            except TemplateDoesNotExist:
                pass
            else:
                email_message.attach_alternative(message_html, "text/html")

        try:
            email_message.send()
        except Exception as e:
            self.stdout.write(self.style.ERROR(e))
        else:
            if verbosity >= 2:
                self.stdout.write(self.style.SUCCESS(f"Notification email sent to {user}!"))

        sleep(delay)

    def handle(self, *args, **options):
        if options["time_delta"]:
            notify_date = datetime.today() + timedelta(days=options["time_delta"])
        else:
            notify_date = datetime.today()

        runs = Run.objects.filter(start=notify_date).count()

        if runs > 0:
            if options["verbosity"] >= 2:
                self.stdout.write(f"Found {runs} run(s) starting {notify_date.date()}.")

            for run in Run.objects.filter(start=notify_date).all():
                if options["verbosity"] >= 1:
                    users_count = run.users.count()

                    if run.manager:
                        users_count += 1

                    self.stdout.write(f"{run} has ", ending="")
                    self.stdout.write(self.style.SUCCESS(f"{users_count} user(s) that will be notified."))

                if options["verbosity"] >= 2:
                    self.stdout.write("Manager: ", ending="")
                    self.stdout.write(self.style.WARNING(run.manager))

                    if run.manager.email:
                        self.notify(
                            run.manager,
                            run,
                            verbosity=options["verbosity"],
                            delay=options["delay"],
                            confirm=options["confirm"],
                        )

                for user in run.users.all():
                    if user.email:
                        self.notify(
                            user,
                            run,
                            verbosity=options["verbosity"],
                            delay=options["delay"],
                            confirm=options["confirm"],
                        )

        else:
            self.stdout.write(self.style.SUCCESS("Nothing to do..."))
