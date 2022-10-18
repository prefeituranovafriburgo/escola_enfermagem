from django.shortcuts import render, redirect
from django.core.checks.messages import Error
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from .forms import *

from selecao.models import Alocacao, Candidato

# Create your views here.

@login_required
def inicio(request):
    return render(request, 'adm/inicio.html')


@login_required
def sair(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('/accounts/logout')
    else:
        return redirect('/accounts/login')

@login_required
def envia_email(request):

    if request.method == 'POST':
        form = BuscaNomeForm(request.POST)

        if form.is_valid():

            nome = form.cleaned_data['nome']

            candidatos = Candidato.objects.filter(nome__icontains=nome)

            if len(candidatos) == 0:
                messages.error(request, 'Nome não cadastrado.')
#                return render(request, "registro_beneficios_busca.html",{"form" : form, 'paroquia_atividade': paroquia_atividade })
            else:
                return render(request, "adm/envia_email.html",{'candidatos': candidatos })

        else:
            # Se teve erro:
            print('Erro: ', form.errors)
            erro_tmp = str(form.errors)
            erro_tmp = erro_tmp.replace('<ul class="errorlist">', '')
            erro_tmp = erro_tmp.replace('</li>', '')
            erro_tmp = erro_tmp.replace('<ul>', '')
            erro_tmp = erro_tmp.replace('</ul>', '')
            erro_tmp = erro_tmp.split('<li>')

            messages.error(request, erro_tmp[1] + ': ' + erro_tmp[2])

    form = BuscaNomeForm()

    return render(request, "adm/busca_nome.html",{"form" : form})


@login_required
def envia(request, id):
    from django.template import Context
    from django.template.loader import render_to_string, get_template
    from django.core.mail import EmailMessage

    candidato = Candidato.objects.get(id=id)

    alocacao = Alocacao.objects.get(candidato=candidato)

    # Envia e-mail

    dados = {
        'nome': alocacao.candidato.nome,
        'cpf': alocacao.candidato.cpf,
        'email': alocacao.candidato.email,
        'sala': alocacao.sala.sala,
        'horario': alocacao.sala.horario.horario,
        'local': alocacao.sala.horario.local.nome,
        'rua': alocacao.sala.horario.local.rua,
        'numero': alocacao.sala.horario.local.numero,
        'bairro': alocacao.sala.horario.local.bairro,
        'cidade': alocacao.sala.horario.local.cidade,
        'chave': alocacao.candidato.chave,
    }

    mensagem = get_template('mail_alocacao.html').render(dados)

    msg = EmailMessage(
        'Local e horário de prova',
        mensagem,
        'Escola de Auxiliares e Técnicos de Enfermagem Nossa Senhora de Fátima - Inscrição <inscricao@sme.novafriburgo.rj.gov.br>',
#        ['loyola@sme.novafriburgo.rj.gov.br'],
#        ['loyola@sme.novafriburgo.rj.gov.br', 'eenfermagemnsf@sme.novafriburgo.rj.gov.br'],
        [alocacao.candidato.email],
    )
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()

    messages.error(request, 'E-Mail enviado.')

    return redirect('adm:envia_email')


@login_required
def relacao_candidatos(request):

    alocacoes = Alocacao.objects.all().order_by('candidato__nome')

    return render(request, "adm/relacao_candidatos.html",{"alocacoes" : alocacoes})


@login_required
def relacao_candidatos_assinatura(request):

    alocacoes = Alocacao.objects.all().order_by('candidato__nome')

    return render(request, "adm/relacao_candidatos_assinatura.html",{"alocacoes" : alocacoes})


@login_required
def relacao_candidatos_porta(request):

    alocacoes = Alocacao.objects.all().order_by('candidato__nome')

    return render(request, "adm/relacao_candidatos_porta.html",{"alocacoes" : alocacoes})
