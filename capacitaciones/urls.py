from django.contrib import admin
from django.urls import path, include
from webui import views as webui_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("p", webui_views.public_page, name="public_page"),
    path("dashboard", webui_views.admin_page, name="admin_page"),
    path("api/", include("training.urls")),
]
