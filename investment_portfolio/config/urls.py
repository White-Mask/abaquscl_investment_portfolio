from django.urls import path, include
from apps.admin_custom.admin import admin_site


urlpatterns = [
    path("admin/", admin_site.urls),
    path("portfolios/", include("apps.portfolios.urls")),
    path("api/", include("api.schemas.openapi")),
]
