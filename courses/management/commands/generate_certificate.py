from datetime import timedelta, datetime

from courses.management.notify_cmd import NotifyCommand
from courses.models import Run, Certificate


class Command(NotifyCommand):
    help = "Generate certificates and notify (send email) to users that are eligible to receive certificate for " \
           "course that has already ended."

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--user_ids", type=str, help="Comma separated list of IDs for which certificates will be generated "
                                         "(no matter if they are eligible for the certificate)."
        )
        parser.add_argument(
            "--run_ids", type=str, help="Comma separated list of Run IDs for which certificates will be generated."
        )
        parser.add_argument("--fake", action="store_true",
                            help="Fake run. Does not store anything to DB, and wont send any emails.")

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

        runs = Run.objects.filter(end__lt=notify_date)

        if run_ids:
            runs = runs.filter(id__in=run_ids)

        if runs.count() > 0:
            if options["verbosity"] >= 2:
                self.stdout.write(f"Found {runs.count()} active run(s).")

            counter = 0

            for run in runs.all():
                start_count = counter
                self.mail_subject = run.get_setting("COURSES_NOTIFY_CERTIFICATE_EMAIL_SUBJECT")
                self.mail_body = run.get_setting("COURSES_NOTIFY_CERTIFICATE_EMAIL_BODY")
                self.mail_body_html = run.get_setting("COURSES_NOTIFY_CERTIFICATE_EMAIL_HTML")

                if options["verbosity"] >= 3:
                    self.stdout.write(self.style.WARNING(run))

                for user in run.users.all():

                    if str(user.id) in user_ids or run.passed(user.id):
                        user_certificates = Certificate.objects.filter(run=run).filter(user=user)

                        if user_certificates.count() == 0:

                            if options["verbosity"] >= 1:
                                self.stdout.write(f"Generating certificate for: ", ending='')

                                if options["verbosity"] >= 3:
                                    self.stdout.write(self.style.SUCCESS(f"{user.first_name} {user.last_name}"),
                                                      ending='')
                                    self.stdout.write(f' (ID: {user.id})')
                                else:
                                    self.stdout.write(self.style.SUCCESS(f"{user.first_name} {user.last_name}"),
                                                      ending='')
                                    self.stdout.write(' in ', ending='')
                                    self.stdout.write(self.style.WARNING(run))

                            if not options["fake"]:
                                cert = Certificate(run=run, user=user)
                                cert.save()

                                self.mail_template_variables["certificate"] = cert
                                self.send_email(user, run, verbosity=options["verbosity"], delay=options["delay"],
                                                confirm=options["confirm"])

                            counter += 1

                if options["verbosity"] >= 3:
                    if counter - start_count == 0:
                        self.stdout.write("No (new) certificates has been generated.")
                    else:
                        self.stdout.write('Generated ', ending='')
                        self.stdout.write(self.style.SUCCESS(counter - start_count), ending='')
                        self.stdout.write(' new certificates.')

            if options["verbosity"] >= 1:
                self.stdout.write(self.style.SUCCESS(f"Total: {counter}"), ending='')
                self.stdout.write(" (new) certificates has been generated.")
        else:
            self.stdout.write(self.style.SUCCESS("Nothing to do..."))

        if options["fake"] and options["verbosity"] >= 1:
            self.stdout.write(self.style.ERROR("FAKE: Nothing has been stored to DB and NO email was send!"))

        super().handle(*args, **options)
