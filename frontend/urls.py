from django.urls import path

from . import views

app_name = 'frontend'

urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),
    path('about_us/', views.AboutUsView.as_view(), name="about_us"),
    path('contact_us/', views.ContactUsView.as_view(), name="contact_us"),
    path('login/', views.LoginUserView.as_view(), name="login"),
    path('register/', views.RegisterUserView.as_view(), name="register"),
]