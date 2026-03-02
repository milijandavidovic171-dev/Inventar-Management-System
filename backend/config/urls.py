from django.contrib import admin
from django.urls import path
from inventar_app.views import portfolio_view, ims_view
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('portfolio/', portfolio_view, name='portfolio'),
    path('ims/', ims_view, name='ims'),
    path('', TemplateView.as_view(template_name='template.html'), name='home'),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)