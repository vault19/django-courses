from courses.models import Course, Category


def get_course(course_slug):
    course = Course.objects.get(slug=course_slug)
    return course


def get_category(category_slug):
    category = Category.objects.get(slug=category_slug)
    return category


def get_public_courses(category_slug=None):
    if category_slug is None:
        courses = Course.objects_no_relations.filter(state="O").order_by("order")
    else:
        category = get_category(category_slug)
        courses = Course.objects_no_relations.filter(state="O", categories__in=[category]).order_by("order")

    return courses
