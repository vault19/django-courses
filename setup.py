import os
from setuptools import find_packages, setup
from courses import __version__ as VERSION, __author__ as AUTHOR

with open(os.path.join(os.path.dirname(__file__), "README.rst")) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="django-courses",
    version=VERSION,
    install_requires=["django", "django-autoslug", "django-bootstrap-v5", "django-embed-video", "django-markdownify"],
    packages=find_packages(),
    include_package_data=True,
    license="MIT License",
    description="Courses is a simple Django app to manage online courses (education).",
    long_description=README,
    long_description_content_type="text/x-rst",
    url="https://github.com/vault19/django-courses",
    author=AUTHOR,
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
