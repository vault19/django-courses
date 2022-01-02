from courses.settings import BASE_TEMPLATE, TEMPLATE_THEME_DIR


def settings(request):
    return {
        "BASE_TEMPLATE": BASE_TEMPLATE,
        "TEMPLATE_THEME_DIR": TEMPLATE_THEME_DIR,
    }
