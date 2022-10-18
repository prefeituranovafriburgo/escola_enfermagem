from multiprocessing import context
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
import json

from datetime import date

from selecao.models import Downloads, Edital
from .functions import separarLinhas


def index(request):
    return render(request, 'editais/index.html')


def editais(request):
    context={
        'editais': Edital.objects.filter(ativo=True)
    }
    return render(request, 'editais/editais.html', context)

def edital(request, id):
    inscricao=False
    encerrar_inscricao=False
    exibir_resultado=False

    edital=Edital.objects.get(id=id)
    try:
        downloads=Downloads.objects.filter(edital=edital)
    except:
        downloads=[]
    if len(downloads)==0:
        downloads=[]
    today=date.today()    
    
    #Condição para exibir ou não o botão para inscrição
    if edital.dt_inicio_inscricao<=today and edital.dt_final_inscricao>=today:
        inscricao=True    
    else:
        if  edital.dt_final_inscricao<=today:
            encerrar_inscricao=True
        
    #Condição para exibir ou não o resultado do concurso
    if edital.dt_resultado<=today:
        exibir_resultado=True    
        
    
    #Listagem de linhas como vetor para rodar no template
    descricao=separarLinhas(edital.descricao)    

    context={
        'edital': edital,
        'exibir_resultado': exibir_resultado,
        'inscricao': inscricao,
        'encerrar_inscricao': encerrar_inscricao,
        'descricao': descricao,
        'downloads': downloads
    }    
    return render(request, 'editais/edital.html', context)

def resultado(request):
    return render(request, 'editais/resultado.html')

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
