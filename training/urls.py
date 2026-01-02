from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path("auth/login", views.login_view, name="login"),
    # Public QR flows
    path("public/qr/resolve", views.public_qr_resolve, name="public_qr_resolve"),
    path("public/register", views.public_register, name="public_register"),
    path("public/pretest", views.public_test, {"qtype":"PRE"}, name="public_pretest"),
    path("public/pretest/submit", views.public_submit, {"qtype":"PRE"}, name="public_pretest_submit"),
    path("public/identify", views.public_identify, name="public_identify"),
    path("public/posttest", views.public_test, {"qtype":"POST"}, name="public_posttest"),
    path("public/posttest/submit", views.public_submit, {"qtype":"POST"}, name="public_posttest_submit"),

    # Admin catalogs
    path("admin/catalog/courses", views.admin_catalog_courses, name="admin_catalog_courses"),
    path("admin/catalog/sites", views.admin_catalog_sites, name="admin_catalog_sites"),

    # Admin reports
    path("admin/reports/results", views.admin_report_results, name="admin_report_results"),
    path("admin/courses/<int:course_id>/qr", views.admin_generate_qr, name="admin_generate_qr"),
]
