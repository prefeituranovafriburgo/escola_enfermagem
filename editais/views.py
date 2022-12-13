from multiprocessing import context
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponse
import json

from datetime import date

from selecao.models import Downloads, Edital, Nota
from .functions import separarLinhas


def index(request):
    return render(request, 'editais/index.html')


def editais(request):
    context = {
        'editais': Edital.objects.filter(ativo=True)
    }
    return render(request, 'editais/editais.html', context)


def edital(request, id):
    inscricao = False
    encerrar_inscricao = False
    exibir_resultado = False

    edital = Edital.objects.get(id=id)
    try:
        downloads = Downloads.objects.filter(edital=edital)
    except:
        downloads = []
    if len(downloads) == 0:
        downloads = []
    today = date.today()

    # Condição para exibir ou não o botão para inscrição
    if edital.dt_inicio_inscricao <= today and edital.dt_final_inscricao >= today:
        inscricao = True
    else:
        if edital.dt_final_inscricao <= today:
            encerrar_inscricao = True

    # Condição para exibir ou não o resultado do concurso
    if edital.dt_resultado <= today:
        exibir_resultado = True

    # Listagem de linhas como vetor para rodar no template
    descricao = separarLinhas(edital.descricao)

    context = {
        'edital': edital,
        'exibir_resultado': exibir_resultado,
        'inscricao': inscricao,
        'encerrar_inscricao': encerrar_inscricao,
        'descricao': descricao,
        'downloads': downloads
    }
    return render(request, 'editais/edital.html', context)


def resultado(request):

    # edital = Edital.objects.get(id=id)

    # if(edital.dt_resultado > date.today()):
        # return redirect('/')
        
    # notas = Nota.objects.order_by('nota').filter(candidato__edital=edital)

#     notas_normais = Nota.objects.raw('''
#     select selecao_candidato.id, nome, nota,
#     -- concat(deficiencia, ensino_fundamental_publico, ensino_medio_publico, renda_bruta, autodeclaracao) as codigo_vaga_reservada,
#     floor((LENGTH(concat(deficiencia, ensino_fundamental_publico, ensino_medio_publico, renda_bruta, autodeclaracao)) 
#     - LENGTH(REPLACE(concat(deficiencia, ensino_fundamental_publico, ensino_medio_publico, renda_bruta, autodeclaracao), 'S', '')))/LENGTH('S'))
#     as pontuação,
#     TIMESTAMPDIFF(YEAR, dt_nascimento, CURDATE()) as idade,
#     dt_nascimento
#     from selecao_candidato
#      join selecao_nota on (selecao_candidato.id = selecao_nota.candidato_id)
#     where floor((LENGTH(concat(deficiencia, ensino_fundamental_publico, ensino_medio_publico, renda_bruta, autodeclaracao)) 
#     - LENGTH(REPLACE(concat(deficiencia, ensino_fundamental_publico, ensino_medio_publico, renda_bruta, autodeclaracao), 'S', '')))/LENGTH('S')) = 0
#     group by selecao_candidato.id
#     order by nota desc, pontuação desc, idade;
# ''')
#     for i in notas_normais:
#         print(i.nome)
#     notas_classificados = notas_normais[:edital.vagas -
#                                         edital.vagas_reservadas]
#     notas_nao_classificados = notas_normais[edital.vagas -
#                                             edital.vagas_reservadas:]

#     notas_reservadas = Nota.objects.raw('''
#     select selecao_candidato.id, nome, nota,
#     -- concat(deficiencia, ensino_fundamental_publico, ensino_medio_publico, renda_bruta, autodeclaracao) as codigo_vaga_reservada,
#     floor((LENGTH(concat(deficiencia, ensino_fundamental_publico, ensino_medio_publico, renda_bruta, autodeclaracao)) 
#     - LENGTH(REPLACE(concat(deficiencia, ensino_fundamental_publico, ensino_medio_publico, renda_bruta, autodeclaracao), 'S', '')))/LENGTH('S'))
#     as pontuação,
#     TIMESTAMPDIFF(YEAR, dt_nascimento, CURDATE()) as idade,
#     dt_nascimento
#     from selecao_candidato
#      join selecao_nota on (selecao_candidato.id = selecao_nota.candidato_id)
#     where floor((LENGTH(concat(deficiencia, ensino_fundamental_publico, ensino_medio_publico, renda_bruta, autodeclaracao)) 
#     - LENGTH(REPLACE(concat(deficiencia, ensino_fundamental_publico, ensino_medio_publico, renda_bruta, autodeclaracao), 'S', '')))/LENGTH('S')) > 0
#     group by selecao_candidato.id
#     order by nota desc, pontuação desc, idade;
# ''')
#     notas_reservadas_classificados = notas_reservadas[:edital.vagas_reservadas]
#     notas_reservadas_nao_classificados = notas_reservadas[edital.vagas_reservadas:]

#     context = {
#         'edital': edital,
#         'notas_normais': notas_normais,
#         'notas_reservadas': notas_reservadas,
#         'notas_classificados': notas_classificados,
#         'notas_nao_classificados': notas_nao_classificados,
#         'notas_reservadas_classificados': notas_reservadas_classificados,
#         'notas_reservadas_nao_classificados': notas_reservadas_nao_classificados,
#         'n_vagas_normais': edital.vagas - edital.vagas_reservadas
#     }
    return render(request, 'editais/resultado.html')


def resultados(request):
    context = {
        'editais': Edital.objects.filter(dt_resultado__lte=date.today()),
    }
    return render(request, 'editais/resultados.html', context)


def login_view(request):
    context = {}
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if "next" in request.GET:
                return redirect(request.GET.get('next'))
            return redirect('/')
        else:
            context = {
                'error': True,
            }

    return render(request, 'registration/login.html', context)
