from django.urls import path
from . import views

app_name='adm'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('envia_email', views.envia_email, name='envia_email'),
    path('envia/<int:id>', views.envia, name='envia'),
    path('relacao_candidatos/<id>/imprimir-lista', views.relacao_candidatos, name='relacao_candidatos'),
    path('relacao_candidatos', views.adm_relacao_candidatos, name='adm_relacao_candidatos'),
    path('relacao_candidatos/<id>/assinatura', views.relacao_candidatos_assinatura, name='relacao_candidatos_assinatura'),
    path('relacao_candidatos/<id>/porta', views.relacao_candidatos_porta, name='relacao_candidatos_porta'),
    path('sair', views.sair, name='sair'),
]