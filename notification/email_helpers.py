from django.templatetags.static import static

# def build_logo_url(request):
#     scheme = 'https' if request.is_secure() else 'http'
#     return f"{scheme}://{request.get_host()}" + static('frontend/img/logo-new.png')


def build_logo_url():
    logo_url = "https://res.cloudinary.com/dbtdu0kwo/image/upload/v1749736735/dgpmo9wrk1bxpi4wcjom.png"
    return logo_url
