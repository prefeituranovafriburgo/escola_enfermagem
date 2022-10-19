from django.urls import path
from . import views

app_name='selecao'

urlpatterns = [
    path('inicio_teste', views.inicio_teste, name='inicio_teste'),
    #
    path('', views.inicio, name='inicio'),
    path('cadastro/46320<id>82', views.cadastro, name='cadastro'),
    path('imprime/<str:chave>', views.imprime, name='imprime'),
    path('consulta', views.consulta, name='consulta'),
    path('consulta_chave/<str:chave>', views.consulta_chave, name='consulta_chave'),
    path('cadastro_corrige/<str:chave>', views.cadastro_corrige, name='cadastro_corrige'),
    path('contato', views.contato, name='contato'),
    path('alocacao', views.alocacao, name='alocacao'),
    path('divulga', views.divulga, name='divulga'),
    path('confirmacao/<str:chave>', views.confirmacao, name='confirmacao'),
    #
#    path('corrige_nome', views.corrige_nome, name='corrige_nome'),
]