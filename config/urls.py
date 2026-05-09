from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from drf_yasg.views import get_schema_view
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Self Study Platform API",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/', include('courses.urls')),
    path('swagger/', schema_view.with_ui('swagger'), name='swagger'),
    path('redoc/', schema_view.with_ui('redoc'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

