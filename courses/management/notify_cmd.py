import os
import requests

from time import sleep

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string

from courses.settings import COURSES_EMAIL_SUBJECT_PREFIX


class NotifyCommand(BaseCommand):
    mail_subject = None
    mail_body = None
    mail_body_html = None
    mail_template_variables = {}

    def add_arguments(self, parser):
        parser.add_argument("--time-delta", type=int, help="Time delta (in days) for comparasion adjustments.")
        parser.add_argument(
            "--delay", nargs="?", type=int, help="Time delay (in seconds) between each email.", default=0
        )
        parser.add_argument("--confirm", action="store_true", help="Confirm user prompt to send out emails.")

    def notify_users(self, run, options):
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
            self.send_email(
                run.manager,
                run,
                verbosity=options["verbosity"],
                delay=options["delay"],
                confirm=options["confirm"],
            )

        for user in run.users.all():
            if user.email:
                self.send_email(
                    user,
                    run,
                    verbosity=options["verbosity"],
                    delay=options["delay"],
                    confirm=options["confirm"],
                )

    def send_email(self, user, run, verbosity=1, delay=0, confirm=False):
        if not confirm:
            self.stdout.write(f"Do you really want to send notification email to: {user} ?")
            user_input = input()

            if user_input.lower() != "y":
                self.stdout.write(self.style.WARNING("Confirmation failed! No email is send..."))
                return

        self.mail_template_variables["user"] = user
        self.mail_template_variables["course_run"] = run

        subject = COURSES_EMAIL_SUBJECT_PREFIX + render_to_string(self.mail_subject, self.mail_template_variables)
        # Email subject *must not* contain newlines
        subject = "".join(subject.splitlines())
        message = render_to_string(self.mail_body, self.mail_template_variables)

        email_message = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

        if self.mail_body_html:
            try:
                message_html = render_to_string(self.mail_body_html, self.mail_template_variables)
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

    def notify_healthchecks(self):
        if os.getenv("HEALTHCHECKS", None):
            r = requests.get(os.getenv("HEALTHCHECKS"))
            self.stdout.write("Acknoledge healthchecks.io: ", ending="")
            self.stdout.write(self.style.SUCCESS(r.text))

    def handle(self, *args, **options):
        self.notify_healthchecks()
