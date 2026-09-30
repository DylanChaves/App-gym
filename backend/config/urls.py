from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("technical-admin/", admin.site.urls),
    path("api/", include("apps.users.urls")),
    path("api/audit/", include("apps.audit.urls")),
]
