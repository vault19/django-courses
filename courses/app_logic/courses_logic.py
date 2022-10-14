from courses.models import Course, Category, Lecture, Chapter


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


class DuplicateCourse:
    def __init__(self, course):
        self.course = course
        self.old_course_id = course.id

    def execute(self):
        self.course.pk = None
        self.course._state.adding = True
        self.course.title = f"Copy of {self.course.title}"
        self.course.save()
        print(self.course)

        chapters = Chapter.objects.filter(course=self.old_course_id)
        for chapter in chapters:
            old_chapter_id = chapter.pk
            chapter.pk = None
            chapter._state.adding = True
            chapter.course = self.course
            chapter.save()

            lectures = Lecture.objects.filter(chapter=old_chapter_id)
            for lecture in lectures:
                lecture.pk = None
                lecture._state.adding = True
                lecture.chapter = chapter
                lecture.save()
