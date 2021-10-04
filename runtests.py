import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner


def run_tests(execute_tests=("courses.tests",)):
    # Run tests
    os.environ['DJANGO_SETTINGS_MODULE'] = 'test_project.settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()

    failures = test_runner.run_tests(execute_tests)

    if failures:
        sys.exit(bool(failures))


if __name__ == "__main__":

    if len(sys.argv) == 1 or sys.argv[1] in ['-a', '--all']:
        tests = (
            'courses.tests',
        )
    else:
        tests = ['tests.{}'.format(arg) for arg in sys.argv[1:]]

    run_tests(execute_tests=tests)
