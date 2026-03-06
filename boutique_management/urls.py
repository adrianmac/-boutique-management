from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.http import JsonResponse

urlpatterns = [
    path("health/", lambda request: JsonResponse({"status": "ok"}), name="health_check"),
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    # Explicit paths to match settings.LOGIN_URL
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
