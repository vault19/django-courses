from django.core.management.base import BaseCommand

from courses.models import Submission


class Command(BaseCommand):
    help = "ONE Time command to calculate missing data. It will go through ALL Submissions and calculate " \
           "'video_watched_percent' if missing, however the lecture has to have 'video_duration' stored in metadata."

    def handle(self, *args, **options):
        for submission in Submission.objects.all():

            if submission.metadata and "watched_video_time_range" in submission.metadata:
                if submission.lecture.metadata and 'video_duration' in submission.lecture.metadata:
                    video_watched = 0

                    for video_range in submission.metadata["watched_video_time_range"]:
                        video_watched += video_range[1] - video_range[0]

                    video_watched_percent = video_watched / submission.lecture.metadata['video_duration'] * 100
                    submission.metadata['video_watched_percent'] = round(video_watched_percent, 1)
                    submission.save()

        self.stdout.write(self.style.SUCCESS('Done. Bye!'))
