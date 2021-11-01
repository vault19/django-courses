from datetime import timedelta, datetime

from courses.management.notify_cmd import NotifyCommand
from courses.models import Run, Certificate


class Command(NotifyCommand):
    help = "Notify (send email) users that new chapter has opened (chapter start == today +/- time_delta)."

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--user_ids", type=str, help="Comma separated list of IDs for which certificates will be generated."
        )
        parser.add_argument(
            "--run_ids", type=str, help="Comma separated list of Run IDs for which certificates will be generated."
        )

    def handle(self, *args, **options):
        if options["time_delta"]:
            notify_date = datetime.today() + timedelta(days=options["time_delta"])
            notify_date = notify_date.date()
        else:
            notify_date = datetime.today().date()

        run_ids = []
        user_ids = []

        if options["run_ids"]:
            run_ids = options["run_ids"].split(",")

        if options["user_ids"]:
            user_ids = options["user_ids"].split(",")

        runs = Run.objects.filter(start__lt=datetime.today()).filter(end__gt=datetime.today())

        if run_ids:
            runs = runs.filter(id__in=run_ids)

        if runs.count() > 0:
            if options["verbosity"] >= 2:
                self.stdout.write(f"Found {runs.count()} active run(s).")

            for run in runs.all():
                counter = 0
                self.mail_subject = run.get_setting("COURSES_NOTIFY_CERTIFICATE_EMAIL_SUBJECT")
                self.mail_body = run.get_setting("COURSES_NOTIFY_CERTIFICATE_EMAIL_BODY")
                self.mail_body_html = run.get_setting("COURSES_NOTIFY_CERTIFICATE_EMAIL_HTML")

                for user in run.users.all():
                    create_cert = False

                    if not user_ids:
                        # TODO: Define automatic completion conditions!
                        create_cert = True
                    if str(user.id) in user_ids:
                        create_cert = True

                    if create_cert:
                        self.mail_template_variables["certificate"] = Certificate.objects.get_or_create(
                            run=run, user=user
                        )[0]
                        self.send_email(user, run, verbosity=1, delay=0, confirm=options["confirm"])
                        counter += 1

                if counter == 0 and options["verbosity"] >= 1:
                    self.stdout.write(f"{run} hasnt any chapter starting {notify_date}.")

        else:
            self.stdout.write(self.style.SUCCESS("Nothing to do..."))

        super().handle(*args, **options)
