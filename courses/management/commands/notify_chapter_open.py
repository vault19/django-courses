from datetime import timedelta, datetime

from courses.management.notify_cmd import NotifyCommand
from courses.models import Run


class Command(NotifyCommand):
    help = "Notify (send email) users that new chapter has opened (chapter start == today +/- time_delta)."

    def handle(self, *args, **options):
        if options["time_delta"]:
            notify_date = datetime.today() + timedelta(days=options["time_delta"])
            notify_date = notify_date.date()
        else:
            notify_date = datetime.today().date()

        runs = Run.objects.filter(start__lte=datetime.today()).filter(end__gt=datetime.today())

        if runs.count() > 0:
            if options["verbosity"] >= 2:
                self.stdout.write(f"Found {runs.count()} active run(s).")

            for run in runs.all():
                counter = 0

                for chapter in run.course.chapter_set.all():
                    start, end = chapter.get_run_dates(run)

                    self.mail_template = chapter.mail_chapter_open

                    if start == notify_date:
                        if options["verbosity"] >= 1:
                            self.stdout.write(f"{run}: {chapter} starts {start}.")

                        counter += 1
                        self.mail_template_variables["chapter"] = chapter
                        self.mail_template_variables["chapter_start"] = start
                        self.mail_template_variables["chapter_end"] = end

                        self.notify_users(run, options)

                if counter == 0 and options["verbosity"] >= 1:
                    self.stdout.write(f"{run} hasnt any chapter starting {notify_date}.")

        else:
            self.stdout.write(self.style.SUCCESS("Nothing to do..."))

        super().handle(*args, **options)
