from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("users/", include("users.urls")),
    path("meals/", include("meals.urls")),
    path("planner/", include("planner.urls")),
    path("shopping/", include("shopping.urls")),
    path("health/", include("health.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
