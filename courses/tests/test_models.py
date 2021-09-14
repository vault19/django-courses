from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from courses.models import Run


class RunTest(TestCase):
    fixtures = ['test_data.json']

    def test_clean_method(self):
        """
        Test all model validations before saving the data into DB.
        """
        run = Run.objects.get(id=1)
        self.assertEqual(run.limit, 30)
        self.assertEqual(run.users.count(), 2)

        run.limit = 0  # Unlimited subscriptions
        self.assertIsNone(run.clean())

        run.limit = 1
        with self.assertRaises(ValidationError, msg="Subscribed user's limit has been reached."):
            run.clean()

        run.limit = 2
        self.assertIsNone(run.clean())

        user = User.objects.get(id=3)
        run.users.add(user)

        with self.assertRaises(ValidationError, msg="Subscribed user's limit has been reached."):
            run.clean()

    def test_save_method(self):
        """
        Test save data to DB. We want to check that validations are applied correctly.
        """
        run = Run.objects.get(id=1)
        self.assertEqual(run.limit, 30)
        self.assertEqual(run.users.count(), 2)

        user = User.objects.get(id=3)
        run.users.add(user)
        self.assertEqual(run.users.count(), 3)

        run.limit = 2
        with self.assertRaises(ValidationError, msg="Subscribed user's limit has been reached."):
            run.save()

        run.limit = 3
        run.save()
        self.assertEqual(run.users.count(), 3)

        user = User.objects.get(id=4)
        run.users.add(user)
        self.assertEqual(run.users.count(), 4)

        with self.assertRaises(ValidationError, msg="Subscribed user's limit has been reached."):
            run.save()

        run.limit = 0  # Unlimited subscriptions
        run.save()
        self.assertEqual(run.users.count(), 4)
