from django.shortcuts import render, redirect
from django.core.checks.messages import Error
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from .forms import *

from selecao.models import Alocacao, Candidato, Edital

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
def relacao_candidatos(request, id):
    try:
        edital = Edital.objects.get(id=id)
        # Ordena por sala primeiro e depois por nome do candidato
        alocacoes = Alocacao.objects.filter(edital=edital).select_related(
            'candidato', 'sala', 'sala__horario'
        ).order_by('sala__id', 'candidato__nome')
    except Edital.DoesNotExist:
        return redirect('adm:adm_relacao_candidatos')

    return render(request, "adm/relacao_candidatos.html", {"alocacoes": alocacoes})

@login_required
def adm_relacao_candidatos(request):

    if request.method=='POST':
        context={
            "edital" : Edital.objects.get(id=request.POST['edital'])
            }
        return render(request, "adm/adm_relacao_candidatos_opcoes.html", context)

    editais=Edital.objects.all()
    context={"editais" : editais}

    return render(request, "adm/adm_relacao_candidatos.html", context)


@login_required
def relacao_candidatos_assinatura(request, id):
    try:
        edital = Edital.objects.get(id=id)
        # Ordena por sala primeiro e depois pelo nome do candidato
        alocacoes = Alocacao.objects.filter(edital=edital).select_related(
            'candidato', 'sala', 'sala__horario'
        ).order_by('sala__id', 'candidato__nome')
    except Edital.DoesNotExist:
        return redirect('adm:adm_relacao_candidatos')

    return render(
        request,
        "adm/relacao_candidatos_assinatura.html",
        {"alocacoes": alocacoes}
    )


@login_required
def relacao_candidatos_porta(request, id):
    try:
        edital = Edital.objects.get(id=id)
        # Ordena por sala primeiro e depois pelo nome do candidato
        alocacoes = Alocacao.objects.filter(edital=edital).select_related(
            'candidato', 'sala', 'sala__horario'
        ).order_by('sala__id', 'candidato__nome')
    except Edital.DoesNotExist:
        return redirect('adm:adm_relacao_candidatos')

    return render(
        request,
        "adm/relacao_candidatos_porta.html",
        {"alocacoes": alocacoes}
    )

@login_required
def candidatos_lista(request):
    campo = request.GET.get('campo', '')  # ID, nome, cpf
    busca = request.GET.get('busca', '')  # texto digitado
    candidatos = Candidato.objects.all().order_by('id')

    if campo and busca:
        if campo == 'id' and busca.isdigit():
            candidatos = candidatos.filter(id=int(busca))
        elif campo == 'nome':
            candidatos = candidatos.filter(nome__icontains=busca)
        elif campo == 'cpf':
            candidatos = candidatos.filter(cpf__icontains=busca)

    return render(request, "adm/candidatos_lista.html", {"candidatos": candidatos, "campo": campo, "busca": busca})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from selecao.models import Candidato

@csrf_exempt
def api_editar_nome_candidato(request):
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            candidato = Candidato.objects.get(id=dados['id'])
            candidato.nome = dados['nome']
            candidato.save()
            return JsonResponse({'status': 200, 'message': 'Nome atualizado com sucesso'})
        except Candidato.DoesNotExist:
            return JsonResponse({'status': 404, 'message': 'Candidato não encontrado'})
        except Exception as e:
            return JsonResponse({'status': 500, 'message': f'Erro: {str(e)}'})
    return JsonResponse({'status': 405, 'message': 'Método não permitido'})

from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from selecao.models import Edital, Nota

@login_required
def classificacao_resultado(request, edital_id):

    # Apenas superusuários
#    if not request.user.is_superuser:
#        return HttpResponseForbidden("Você não tem permissão para acessar esta página.")

    edital = Edital.objects.get(id=edital_id)

    # Impede acesso antes da data
    #if edital.dt_resultado > date.today():
     #   return redirect('/')

    # ---------------------------
    #      QUERY NORMAL
    # ---------------------------
    notas_normais = Nota.objects.raw('''
        SELECT
            c.id,
            c.nome,
            n.nota,
            FLOOR(
                (LENGTH(CONCAT(c.deficiencia, c.ensino_fundamental_publico,
                               c.ensino_medio_publico, c.renda_bruta, c.autodeclaracao))
                 - LENGTH(REPLACE(CONCAT(c.deficiencia, c.ensino_fundamental_publico,
                                          c.ensino_medio_publico, c.renda_bruta, c.autodeclaracao), 'S', ''))
                ) / LENGTH('S')
            ) AS pontuacao,
            TIMESTAMPDIFF(YEAR, c.dt_nascimento, CURDATE()) AS idade,
            c.dt_nascimento
        FROM selecao_candidato c
        JOIN selecao_nota n ON c.id = n.candidato_id
        WHERE FLOOR(
                (LENGTH(CONCAT(c.deficiencia, c.ensino_fundamental_publico,
                               c.ensino_medio_publico, c.renda_bruta, c.autodeclaracao))
                 - LENGTH(REPLACE(CONCAT(c.deficiencia, c.ensino_fundamental_publico,
                                          c.ensino_medio_publico, c.renda_bruta, c.autodeclaracao), 'S', ''))
                ) / LENGTH('S')
            ) = 0
        ORDER BY n.nota DESC, pontuacao DESC, idade DESC;
    ''')

    notas_classificados = notas_normais[:edital.vagas - edital.vagas_reservadas]
    notas_nao_classificados = notas_normais[edital.vagas - edital.vagas_reservadas:]

    # ---------------------------
    #      QUERY RESERVADAS
    # ---------------------------
    notas_reservadas = Nota.objects.raw('''
        SELECT
            c.id,
            c.nome,
            n.nota,
            FLOOR(
                (LENGTH(CONCAT(c.deficiencia, c.ensino_fundamental_publico,
                               c.ensino_medio_publico, c.renda_bruta, c.autodeclaracao))
                 - LENGTH(REPLACE(CONCAT(c.deficiencia, c.ensino_fundamental_publico,
                                          c.ensino_medio_publico, c.renda_bruta, c.autodeclaracao), 'S', ''))
                ) / LENGTH('S')
            ) AS pontuacao,
            TIMESTAMPDIFF(YEAR, c.dt_nascimento, CURDATE()) AS idade,
            c.dt_nascimento
        FROM selecao_candidato c
        JOIN selecao_nota n ON c.id = n.candidato_id
        WHERE FLOOR(
                (LENGTH(CONCAT(c.deficiencia, c.ensino_fundamental_publico,
                               c.ensino_medio_publico, c.renda_bruta, c.autodeclaracao))
                 - LENGTH(REPLACE(CONCAT(c.deficiencia, c.ensino_fundamental_publico,
                                          c.ensino_medio_publico, c.renda_bruta, c.autodeclaracao), 'S', ''))
                ) / LENGTH('S')
            ) > 0
        ORDER BY n.nota DESC, pontuacao DESC, idade DESC;
    ''')

    notas_reservadas_classificados = notas_reservadas[:edital.vagas_reservadas]
    notas_reservadas_nao_classificados = notas_reservadas[edital.vagas_reservadas:]

    context = {
        'edital': edital,
        'notas_classificados': notas_classificados,
        'notas_nao_classificados': notas_nao_classificados,
        'notas_reservadas_classificados': notas_reservadas_classificados,
        'notas_reservadas_nao_classificados': notas_reservadas_nao_classificados,
    }

    return render(request, "adm/classificacao_resultado.html", context)

from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse, HttpResponseForbidden

@login_required
def classificacao_pdf(request, edital_id):

    if not request.user.is_superuser:
        return HttpResponseForbidden("Sem permissão.")

    edital = Edital.objects.get(id=edital_id)

    # ================================
    # AMPLA CONCORRÊNCIA
    # ================================
    notas_normais = list(Nota.objects.raw('''
        SELECT
            c.id,
            c.nome,
            n.nota,
            FLOOR(
                (LENGTH(CONCAT(c.deficiencia, c.ensino_fundamental_publico,
                               c.ensino_medio_publico, c.renda_bruta, c.autodeclaracao))
                 - LENGTH(REPLACE(CONCAT(c.deficiencia, c.ensino_fundamental_publico,
                                          c.ensino_medio_publico, c.renda_bruta, c.autodeclaracao), 'S', ''))
                ) / LENGTH('S')
            ) AS pontuacao,
            TIMESTAMPDIFF(YEAR, c.dt_nascimento, CURDATE()) AS idade
        FROM selecao_candidato c
        JOIN selecao_nota n ON c.id = n.candidato_id
        WHERE FLOOR(
                (LENGTH(CONCAT(c.deficiencia, c.ensino_fundamental_publico,
                               c.ensino_medio_publico, c.renda_bruta, c.autodeclaracao))
                 - LENGTH(REPLACE(CONCAT(c.deficiencia, c.ensino_fundamental_publico,
                                          c.ensino_medio_publico, c.renda_bruta, c.autodeclaracao), 'S', ''))
                ) / LENGTH('S')
            ) = 0
        ORDER BY n.nota DESC, pontuacao DESC, idade DESC;
    '''))

    # Separação
    notas_classificados = notas_normais[:edital.vagas - edital.vagas_reservadas]
    notas_nao_classificados = notas_normais[edital.vagas - edital.vagas_reservadas:]

    # Numeração correta
    for i, n in enumerate(notas_classificados, start=1):
        n.colocacao = i

    start = len(notas_classificados) + 1
    for i, n in enumerate(notas_nao_classificados, start=start):
        n.colocacao = i

    # ================================
    # RESERVADAS
    # ================================
    notas_reservadas = list(Nota.objects.raw('''
        SELECT
            c.id,
            c.nome,
            n.nota,
            FLOOR(
                (LENGTH(CONCAT(c.deficiencia, c.ensino_fundamental_publico,
                               c.ensino_medio_publico, c.renda_bruta, c.autodeclaracao))
                 - LENGTH(REPLACE(CONCAT(c.deficiencia, c.ensino_fundamental_publico,
                                          c.ensino_medio_publico, c.renda_bruta, c.autodeclaracao), 'S', ''))
                ) / LENGTH('S')
            ) AS pontuacao,
            TIMESTAMPDIFF(YEAR, c.dt_nascimento, CURDATE()) AS idade
        FROM selecao_candidato c
        JOIN selecao_nota n ON c.id = n.candidato_id
        WHERE FLOOR(
                (LENGTH(CONCAT(c.deficiencia, c.ensino_fundamental_publico,
                               c.ensino_medio_publico, c.renda_bruta, c.autodeclaracao))
                 - LENGTH(REPLACE(CONCAT(c.deficiencia, c.ensino_fundamental_publico,
                                          c.ensino_medio_publico, c.renda_bruta, c.autodeclaracao), 'S', ''))
                ) / LENGTH('S')
            ) > 0
        ORDER BY n.nota DESC, pontuacao DESC, idade DESC;
    '''))

    notas_reservadas_classificados = notas_reservadas[:edital.vagas_reservadas]
    notas_reservadas_nao_classificados = notas_reservadas[edital.vagas_reservadas:]

    # Numeração reservadas (começa em 1 de novo)
    for i, n in enumerate(notas_reservadas_classificados, start=1):
        n.colocacao = i

    start_res = len(notas_reservadas_classificados) + 1
    for i, n in enumerate(notas_reservadas_nao_classificados, start=start_res):
        n.colocacao = i

    # ================================
    # RENDERIZAÇÃO
    # ================================
    html_string = render_to_string(
        "adm/classificacao_pdf.html",
        {
            "edital": edital,
            "notas_classificados": notas_classificados,
            "notas_nao_classificados": notas_nao_classificados,
            "notas_reservadas_classificados": notas_reservadas_classificados,
            "notas_reservadas_nao_classificados": notas_reservadas_nao_classificados,
        }
    )

    pdf = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="classificacao_{edital_id}.pdf"'
    return response
