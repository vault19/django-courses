from courses.settings import BASE_TEMPLATE


def settings(request):
    return {
        "BASE_TEMPLATE": BASE_TEMPLATE,
    }
