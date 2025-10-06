from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('editais.urls')),
    path('administrativo/', include('adm.urls')),
    path('selecao/', include('selecao.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
admin.site.site_header = "SECRETARIA MUNICIPAL DE EDUCAÇÃO"
admin.site.site_title = "PREFEITURA MUNICIPAL DE NOVA FRIBURGO"

