from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from courses.models import Course, Category, Lecture, Chapter, Coupon, RunUsers


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


class CouponNotValidException(Exception):
    pass


class CouponAlreadyAppliedException(Exception):
    pass


class ApplyCoupon:
    def __init__(self, coupon_slug, run_user):
        self.coupon_slug = coupon_slug
        self.run_user = run_user

    def execute(self):
        coupon = Coupon.objects.get(slug=self.coupon_slug)  # raises an error if Coupon not found

        if self.run_user.run.course not in coupon.courses.all():
            raise CouponNotValidException(_("Specified coupon can not be applied for this course."))

        if coupon.valid_from > timezone.now().date():
            raise CouponNotValidException(_("Specified coupon is not valid yet."))

        if coupon.valid_to < timezone.now().date():
            raise CouponNotValidException(_("Specified coupon is not valid anymore."))

        if coupon.count_usages() >= coupon.limit:
            raise CouponNotValidException(_("Specified coupon is not valid anymore."))

        if self.run_user.discount_coupon or self.run_user.price_before_discount:
            raise CouponAlreadyAppliedException(_("A discount has already been applied to this registration."))

        self.run_user.discount_coupon = coupon
        self.run_user.price_before_discount = self.run_user.price

        if coupon.discount_type == coupon.FLAT_DISCOUNT:
            self.run_user.price = max(0, self.run_user.price - coupon.discount)
        elif coupon.discount_type == coupon.PERCENTAGE_DISCOUNT:
            self.run_user.price = self.run_user.price * (100-coupon.discount)/100

        self.run_user.price = round(self.run_user.price, 2)  # round to two decimal places

        self.run_user.save()
