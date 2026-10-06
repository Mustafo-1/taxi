from django.contrib.auth import views as auth
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("login/", auth.LoginView.as_view(template_name="login.html", redirect_authenticated_user=True), name="login"),
    path("logout/", auth.LogoutView.as_view(), name="logout"),
    path("order/", views.order, name="order"),
    path("order/<int:pk>/", views.order_detail, name="order_detail"),
    path("driver/", views.driver_panel, name="driver_panel"),
]
