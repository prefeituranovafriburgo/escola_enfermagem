from django.contrib import admin
from .models import *

# Register your models here.

class EditalAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome', 'mes', 'ano']
#    list_filter = ['nome']
    search_fields = ['nome', 'id', 'ano', 'mes']

admin.site.register(Edital, EditalAdmin)

admin.site.register(Downloads)

class CandidatoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome', 'cpf', 'dt_nascimento', 'celular', 'deficiencia', 'dt_inclusao']
    list_filter = ['edital','deficiencia']
    search_fields = ['nome', 'id']

admin.site.register(Candidato, CandidatoAdmin)

class LocalAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome', 'dt_inclusao']
#    list_filter = ['nome']
    search_fields = ['nome', 'id']

admin.site.register(Local, LocalAdmin)

class HorarioAdmin(admin.ModelAdmin):
    list_display = ['id', 'local', 'horario', 'dt_inclusao']
    list_filter = ['local']
    search_fields = ['local__nome']

admin.site.register(Horario, HorarioAdmin)

class SalaAdmin(admin.ModelAdmin):
    list_display = ['id', 'horario', 'sala', 'dt_inclusao']
#    list_filter = ['local']
    search_fields = ['sala']

admin.site.register(Sala, SalaAdmin)

class AlocacaoAdmin(admin.ModelAdmin):
    list_display = ['id', 'sala', 'candidato', 'dt_inclusao']
    list_filter = ['sala']
    search_fields = ['candidato__nome']

admin.site.register(Alocacao, AlocacaoAdmin)

class AcessoAdmin(admin.ModelAdmin):
    list_display = ['id', 'candidato', 'ip', 'dt_inclusao']
#    list_filter = ['sala']
    search_fields = ['candidato__nome']

admin.site.register(Acesso, AcessoAdmin)

class NotaAdmin(admin.ModelAdmin):
    list_display = ['nota', 'candidato', 'dt_inclusao']
#    list_filter = ['sala']
    search_fields = ['candidato__nome']

admin.site.register(Nota, NotaAdmin)
