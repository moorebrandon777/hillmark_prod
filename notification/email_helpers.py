from django.templatetags.static import static

def build_logo_url(request):
    scheme = 'https' if request.is_secure() else 'http'
    return f"{scheme}://{request.get_host()}" + static('frontend/img/logo-new.png')
