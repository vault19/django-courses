from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from courses.models import Run


class RunTest(TestCase):
    fixtures = ["test_data.json"]

    def test_is_full(self):
        run = Run.objects.get(id=1)
        self.assertEqual(run.limit, 30)
        self.assertEqual(run.users.count(), 2)

        run.limit = 0  # Unlimited subscriptions
        self.assertEqual(run.is_full, False)

        run.limit = 3
        self.assertEqual(run.is_full, False)

        run.limit = 2
        self.assertEqual(run.is_full, True)

        user = User.objects.get(id=3)
        run.users.add(user)
        self.assertEqual(run.users.count(), 3)
        self.assertEqual(run.is_full, True)

    def test_is_subscribed_in_different_active_run(self):
        run1 = Run.objects.get(id=1)
        user = User.objects.get(id=3)
        self.assertEqual(user in run1.users.all(), False)
        self.assertEqual(run1.is_subscribed_in_different_active_run(user), False)
        run1.users.add(user)
        self.assertEqual(user in run1.users.all(), True)
        self.assertEqual(run1.is_subscribed_in_different_active_run(user), False)

        run2 = Run.objects.get(id=2)
        self.assertEqual(run1.course == run2.course, True)
        self.assertEqual(user in run2.users.all(), False)
        self.assertEqual(run2.is_subscribed_in_different_active_run(user), True)
