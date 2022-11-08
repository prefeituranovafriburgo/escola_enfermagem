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


def resultado(request, id):

    edital = Edital.objects.get(id=id)

    if(edital.dt_resultado >= date.today()):
        return redirect('/')
    notas = Nota.objects.order_by('nota').filter(candidato__edital=edital)

    notas_normais = notas.filter(candidato__deficiencia='N', candidato__autodeclaracao='N', candidato__renda_bruta='N',
                                 candidato__ensino_fundamental_publico='N', candidato__ensino_medio_publico='N')
    notas_classificados = notas_normais[:edital.vagas -
                                        edital.vagas_reservadas]
    notas_nao_classificados = notas_normais[edital.vagas -
                                            edital.vagas_reservadas:]

    notas_reservadas = notas.filter(Q(candidato__deficiencia='S') | Q(candidato__autodeclaracao='S') | Q(
        candidato__renda_bruta='S') | Q(candidato__ensino_fundamental_publico='S') | Q(candidato__ensino_medio_publico='S'))
    notas_reservadas_classificados = notas_reservadas[:edital.vagas_reservadas]
    notas_reservadas_nao_classificados = notas_reservadas[edital.vagas_reservadas:]

    context = {
        'edital': edital,
        'notas_classificados': notas_classificados,
        'notas_nao_classificados': notas_nao_classificados,
        'notas_reservadas_classificados': notas_reservadas_classificados,
        'notas_reservadas_nao_classificados': notas_reservadas_nao_classificados
    }
    return render(request, 'editais/resultado.html', context)


def resultados(request):
    print(Edital.objects.filter(dt_resultado=date.today()))
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
