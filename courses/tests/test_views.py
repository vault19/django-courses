from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from courses.models import Run


class TestRequiredLoginPage(TestCase):
    fixtures = ["test_data.json"]

    def test_redirects(self):
        response = self.client.get("/courses/subscribed/")
        self.assertRedirects(response, "/accounts/login/?next=/courses/subscribed/")

        response = self.client.get("/courses/subscribed/closed/")
        self.assertRedirects(response, "/accounts/login/?next=/courses/subscribed/closed/")

        response = self.client.get("/courses/closed/")
        self.assertRedirects(response, "/accounts/login/?next=/courses/closed/")

        # From fixture
        response = self.client.get("/course/septembrovy-kurz/lekcia-1/")
        self.assertRedirects(response, "/accounts/login/?next=/course/septembrovy-kurz/lekcia-1/")
        # Non Existing
        response = self.client.get("/course/unknown-course/introduction/")
        self.assertRedirects(response, "/accounts/login/?next=/course/unknown-course/introduction/")

        response = self.client.get("/course/septembrovy-kurz/lekcia-1/submission/")
        self.assertRedirects(response, "/accounts/login/?next=/course/septembrovy-kurz/lekcia-1/submission/")

        response = self.client.get("/course/septembrovy-kurz/lekcia-1/filter/V/")
        self.assertRedirects(response, "/accounts/login/?next=/course/septembrovy-kurz/lekcia-1/filter/V/")

        response = self.client.get("/course/septembrovy-kurz/subscribe/")
        self.assertRedirects(response, "/accounts/login/?next=/course/septembrovy-kurz/subscribe/")

        response = self.client.get("/course/septembrovy-kurz/unsubscribe/")
        self.assertRedirects(response, "/accounts/login/?next=/course/septembrovy-kurz/unsubscribe/")

        response = self.client.get("/course/septembrovy-kurz/lekcia-1/uvod-do-kurzu/")
        self.assertRedirects(response, "/accounts/login/?next=/course/septembrovy-kurz/lekcia-1/uvod-do-kurzu/")

        response = self.client.get("/course/septembrovy-kurz/lekcia-1/uvod-do-kurzu/submission/")
        self.assertRedirects(
            response, "/accounts/login/?next=/course/septembrovy-kurz/lekcia-1/uvod-do-kurzu/submission/"
        )


class TestSubscribeUnsubscribePage(TestCase):
    fixtures = ["test_data.json"]

    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.user.set_password("12345")
        self.user.save()

        response = self.client.login(username=self.user.username, password="12345")
        self.assertEqual(True, response)

    def test_GET_methods(self):
        response = self.client.get("/course/septembrovy-kurz/subscribe/", follow=True)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You need to submit subscription form in order to subscribe!")
        self.assertRedirects(response, "/course/septembrovy-kurz/")

        response = self.client.get("/course/septembrovy-kurz/unsubscribe/", follow=True)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You need to submit subscription form in order to unsubscribe!")
        self.assertRedirects(response, "/course/septembrovy-kurz/")

    def test_subscribe(self):
        run_slug = "septembrovy-kurz"
        run = Run.objects.get(slug=run_slug)
        self.assertEqual(run.users.count(), 2)
        self.assertEqual(self.user in run.users.all(), False)

        response = self.client.post(
            f"/course/{run_slug}/subscribe/", {"sender": self.user.username, "run_slug": run_slug}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You have been subscribed to course: %s" % run)

        run = Run.objects.get(slug=run_slug)
        self.assertEqual(self.user in run.users.all(), True)
        self.assertEqual(run.users.count(), 3)

        response = self.client.post(
            f"/course/{run_slug}/subscribe/", {"sender": self.user.username, "run_slug": run_slug}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You are already subscribed to course: %s" % run)
        self.assertEqual(run.users.count(), 3)

    def test_subscribe_to_course_run_with_limit_full(self):
        run_slug = "septembrovy-kurz"
        run = Run.objects.get(slug=run_slug)
        run.limit = 2
        run.save()
        self.assertEqual(run.users.count(), 2)
        self.assertEqual(self.user in run.users.all(), False)

        response = self.client.post(
            f"/course/{run_slug}/subscribe/", {"sender": self.user.username, "run_slug": run_slug}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Subscribed user's limit has been reached.")
        self.assertEqual(run.users.count(), 2)

    def test_subscribe_in_multiple_runs_of_the_same_course(self):
        run_slug = "septembrovy-kurz"
        run = Run.objects.get(slug=run_slug)
        self.assertEqual(self.user in run.users.all(), False)

        response = self.client.post(
            f"/course/{run_slug}/subscribe/", {"sender": self.user.username, "run_slug": run_slug}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You have been subscribed to course: %s" % run)

        run = Run.objects.get(slug=run_slug)
        self.assertEqual(self.user in run.users.all(), True)

        run_slug = "decembrovy-kurz"
        run = Run.objects.get(slug=run_slug)
        self.assertEqual(self.user in run.users.all(), False)

        response = self.client.post(
            f"/course/{run_slug}/subscribe/", {"sender": self.user.username, "run_slug": run_slug}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You are already subscribed in different course run.")

        run = Run.objects.get(slug=run_slug)
        self.assertEqual(self.user in run.users.all(), False)

    def test_subscribe_unknown_run(self):
        run_slug = "unknown-course-run"

        with self.assertRaises(ObjectDoesNotExist):
            run = Run.objects.get(slug=run_slug)

        response = self.client.post(
            f"/course/{run_slug}/subscribe/", {"sender": self.user.username, "run_slug": run_slug}, follow=True
        )
        self.assertEqual(response.status_code, 404)

    def test_unsubscribe_unknown_run(self):
        run_slug = "unknown-course-run"

        with self.assertRaises(ObjectDoesNotExist):
            run = Run.objects.get(slug=run_slug)

        response = self.client.post(
            f"/course/{run_slug}/unsubscribe/", {"sender": self.user.username, "run_slug": run_slug}, follow=True
        )
        self.assertEqual(response.status_code, 404)

    def test_unsubscribe(self):
        run_slug = "septembrovy-kurz"
        run = Run.objects.get(slug=run_slug)

        self.assertEqual(self.user in run.users.all(), False)
        self.assertEqual(run.users.count(), 2)
        run.users.add(self.user)
        run.save()
        self.assertEqual(self.user in run.users.all(), True)
        self.assertEqual(run.users.count(), 3)

        response = self.client.post(
            f"/course/{run_slug}/unsubscribe/", {"sender": self.user.username, "run_slug": run_slug}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You have been unsubscribed from course: %s" % run)
        self.assertEqual(run.users.count(), 2)

        run = Run.objects.get(slug=run_slug)
        self.assertEqual(self.user in run.users.all(), False)

        response = self.client.post(
            f"/course/{run_slug}/unsubscribe/", {"sender": self.user.username, "run_slug": run_slug}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You are not subscribed to the course: %s" % run)
        self.assertEqual(run.users.count(), 2)
