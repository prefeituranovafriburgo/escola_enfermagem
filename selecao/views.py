from django.core.checks.messages import Error
from django.shortcuts import render, redirect
from .forms import *
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

def inicio_teste(request):
    return render(request, 'inicio.html')


def inicio(request):
    from datetime import date, datetime

    hoje = date.today()
    data_inicio = datetime.strptime('18/10/2022', '%d/%m/%Y').date()
    data_fim = datetime.strptime('31/10/2022', '%d/%m/%Y').date()

    data_resultado = datetime.strptime('08/12/2022', '%d/%m/%Y').date()

    if hoje >= data_resultado:
        return render(request, 'inicio_resultado.html')

    if hoje > data_fim:
        return render(request, 'inscricao_encerrada.html')

    if hoje >= data_inicio and hoje <= data_fim:
        return render(request, 'inicio.html')

    return render(request, 'inicio_aguardar.html')


def cadastro(request, id):
    from django.template import Context
    from django.template.loader import render_to_string, get_template
    from django.core.mail import EmailMessage
    import uuid
    from ipware import get_client_ip
    


    try:
        edital=Edital.objects.get(id=id, ativo=True)
    except:
        edital=False
    
    if edital:
        # if date.today() > edital.dt_final_inscricao:
        #     messages.error(request, 'O período de inscrição para este edital já foi encerrado.')
        #     return redirect('/')
        if request.method == 'POST':
            form = CandidatoForm(request.POST, request.FILES)            
            if form.is_valid():                
                cadastro = form.save(commit=False)

                chave = str(uuid.uuid4())
                cadastro.chave = chave

                # Busca IP

                client_ip, is_routable = get_client_ip(request)
                if client_ip is None:
                    # Unable to get the client's IP address
                    print(client_ip)
                    client_ip = '0.0.0.0'
                else:
                    # We got the client's IP address
                    if is_routable:
                        print('sim:', is_routable)
                        # The client's IP address is publicly routable on the Internet
                    else:
                        print('não:', is_routable)
                        # The client's IP address is privat

                cadastro.ip = client_ip

                cadastro.save()

                # Envia e-mail

                dados = {
                    'id': cadastro.id,
                    'nome': cadastro.nome,
                    'dt_nascimento': cadastro.dt_nascimento,
                    'cpf': cadastro.cpf,
                    'celular': cadastro.celular,
                    'tel': cadastro.tel,
                    'email': cadastro.email,
                    'deficiencia': cadastro.deficiencia,
                    'qual_deficiencia': cadastro.qual_deficiencia,
                    'necessidade': cadastro.necessidade,
                    'dt_inclusao': cadastro.dt_inclusao,
                    'ip': cadastro.ip,
                    'edital': edital
                }

                mensagem = get_template('mail.html').render(dados)
                # print(dados)
                msg = EmailMessage(
                    'Confirmação de Inscrição - Escola de Auxiliares e Técnicos de Enfermagem Nossa Senhora de Fátima',
                    mensagem,
                    'Escola de Auxiliares e Técnicos de Enfermagem Nossa Senhora de Fátima - Inscrição <inscricao@sme.novafriburgo.rj.gov.br>',
                    [cadastro.email],
                )
                msg.content_subtype = "html"  # Main content is now text/html
                msg.send()

                return render(request, 'cadastrook.html', { 'chave': chave })

            else:
                # Se teve erro:
                # print('Erro: ', form.errors)
                erro_tmp = str(form.errors)
                erro_tmp = erro_tmp.replace('<ul class="errorlist">', '')
                erro_tmp = erro_tmp.replace('</li>', '')
                erro_tmp = erro_tmp.replace('<ul>', '')
                erro_tmp = erro_tmp.replace('</ul>', '')
                erro_tmp = erro_tmp.split('<li>')

                messages.error(request, erro_tmp[2])

                #print(form)
                #return render(request, 'cadastro.html', { 'form': form, 'id': id, 'nome': edital.nome })
        else:
            form = CandidatoForm(initial={'edital': edital.id})

        return render(request, 'cadastro.html', { 'form': form, 'id': id, 'nome': edital.nome })
    else:
        return redirect ('/')

def imprime(request, chave):
    candidato = Candidato.objects.get(chave=chave)

    return render(request, 'ficha.html', { 'candidato': candidato })


def consulta(request):
    from django.template import Context
    from django.template.loader import render_to_string, get_template
    from django.core.mail import EmailMessage
    import uuid

    if request.method == 'POST':
        form = ConsultaForm(request.POST)

        if form.is_valid():

            cpf = form.cleaned_data['cpf']

            try:
                candidato = Candidato.objects.get(cpf=cpf)
            except ObjectDoesNotExist:
                messages.error(request, 'CPF não cadastrado.')
                return render(request, 'consulta.html', { 'form': form })

            # Envia e-mail

            dados = {
                'id': candidato.id,
                'nome': candidato.nome,
                'cpf': candidato.cpf,
                'email': candidato.email,
                'dt_inclusao': candidato.dt_inclusao,
                'ip': candidato.ip,
                'chave': candidato.chave,
            }

            mensagem = get_template('mail_consulta.html').render(dados)

            msg = EmailMessage(
                'Consulta a inscrição do Processo Seletivo para Curso de Técnico em Enfermagem',
                mensagem,
                'Escola de Auxiliares e Técnicos de Enfermagem Nossa Senhora de Fátima - Inscrição <inscricao@sme.novafriburgo.rj.gov.br>',
                [candidato.email],
            )
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()


            messages.success(request, 'Enviamos um e-mail para o endereço informado na hora da sua inscrição com o link de acesso aos dados de seu cadastro.')

            return redirect ('/')

        else:
            # Se teve erro:
            print('Erro: ', form.errors)
            erro_tmp = str(form.errors)
            erro_tmp = erro_tmp.replace('<ul class="errorlist">', '')
            erro_tmp = erro_tmp.replace('</li>', '')
            erro_tmp = erro_tmp.replace('<ul>', '')
            erro_tmp = erro_tmp.replace('</ul>', '')
            erro_tmp = erro_tmp.split('<li>')

            messages.error(request, erro_tmp[2])

    else:
        form = ConsultaForm()

    return render(request, 'consulta.html', { 'form': form })


def consulta_chave(request, chave):

    try:
        candidato = Candidato.objects.get(chave=chave)
    except ObjectDoesNotExist:
        messages.error(request, 'Chave não cadastrada.')
        return redirect ('/consulta')

    return render(request, 'cadastro_mostra.html', { 'candidato': candidato })



def cadastro_corrige(request, chave):
    from django.template import Context
    from django.template.loader import render_to_string, get_template
    from django.core.mail import EmailMessage
    import uuid
    from ipware import get_client_ip

    try:
        candidato = Candidato.objects.get(chave=chave)
    except ObjectDoesNotExist:
        messages.error(request, 'Chave não cadastrada.')
        return redirect ('/selecao/consulta')


    if request.method == 'POST':
        form = CandidatoForm(request.POST, request.FILES, instance=candidato)

        if form.is_valid():
            cadastro = form.save(commit=False)

            chave = str(uuid.uuid4())
            cadastro.chave = chave

            # Busca IP

            client_ip, is_routable = get_client_ip(request)
            if client_ip is None:
                # Unable to get the client's IP address
                print(client_ip)
                client_ip = '0.0.0.0'
            else:
                # We got the client's IP address
                if is_routable:
                    print('sim:', is_routable)
                    # The client's IP address is publicly routable on the Internet
                else:
                    print('não:', is_routable)
                    # The client's IP address is privat

            cadastro.ip = client_ip

            cadastro.save()

            # Envia e-mail

            dados = {
                'id': cadastro.id,
                'nome': cadastro.nome,
                'dt_nascimento': cadastro.dt_nascimento,
                'cpf': cadastro.cpf,
                'celular': cadastro.celular,
                'tel': cadastro.tel,
                'email': cadastro.email,
                'deficiencia': cadastro.deficiencia,
                'qual_deficiencia': cadastro.qual_deficiencia,
                'necessidade': cadastro.necessidade,
                'dt_inclusao': cadastro.dt_inclusao,
                'ip': cadastro.ip,
            }

            mensagem = get_template('mail.html').render(dados)

            msg = EmailMessage(
                'Correção da inscrição do Processo Seletivo para Curso de Técnico em Enfermagem',
                mensagem,
                'Escola de Auxiliares e Técnicos de Enfermagem Nossa Senhora de Fátima - Inscrição <inscricao@sme.novafriburgo.rj.gov.br>',
                [cadastro.email],
            )
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()

            return render(request, 'cadastrook.html', { 'chave': chave })

        else:
            # Se teve erro:
            print('Erro: ', form.errors)
            erro_tmp = str(form.errors)
            erro_tmp = erro_tmp.replace('<ul class="errorlist">', '')
            erro_tmp = erro_tmp.replace('</li>', '')
            erro_tmp = erro_tmp.replace('<ul>', '')
            erro_tmp = erro_tmp.replace('</ul>', '')
            erro_tmp = erro_tmp.split('<li>')

            messages.error(request, erro_tmp[2])

    else:
        form = CandidatoForm(instance=candidato)

    return render(request, 'cadastro_corrigir.html', { 'form': form, 'id': candidato.edital.id})


def contato(request):
    from django.template import Context
    from django.template.loader import render_to_string, get_template
    from django.core.mail import EmailMessage

    if request.method == 'POST':
        form = ContatoForm(request.POST)

        if form.is_valid():

            # Envia e-mail

            dados = {
                'nome': form.cleaned_data['nome'],
                'cpf': form.cleaned_data['cpf'],
                'celular': form.cleaned_data['celular'],
                'email': form.cleaned_data['email'],
                'duvida': form.cleaned_data['duvida'],
            }

            mensagem = get_template('mail_contato.html').render(dados)

            msg = EmailMessage(
                'Dúvidas',
                mensagem,
                'Escola de Auxiliares e Técnicos de Enfermagem Nossa Senhora de Fátima - Inscrição <inscricao@sme.novafriburgo.rj.gov.br>',
                ['inscricao@sme.novafriburgo.rj.gov.br', 'loyola@sme.novafriburgo.rj.gov.br', 'eenfermagemnsf@sme.novafriburgo.rj.gov.br'],
            )
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()

            messages.error(request, 'E-Mail enviado. Entraremos em contato em breve para sanar sua dúvida.')

            return redirect ('/')

        else:
            # Se teve erro:
            print('Erro: ', form.errors)
            erro_tmp = str(form.errors)
            erro_tmp = erro_tmp.replace('<ul class="errorlist">', '')
            erro_tmp = erro_tmp.replace('</li>', '')
            erro_tmp = erro_tmp.replace('<ul>', '')
            erro_tmp = erro_tmp.replace('</ul>', '')
            erro_tmp = erro_tmp.split('<li>')

            messages.error(request, erro_tmp[2])

    else:
        form = ContatoForm()

    return render(request, 'contato.html', { 'form': form })

from django.http import HttpResponse

def alocacao(request):
    candidatos = Candidato.objects.all().order_by('nome')

    limite_salas = {1: 2, 2: 1, 3: 1, 4: 2, 5: 6}
    sala_ids = [1, 2, 3, 4, 5]

    # Candidatos que precisam ir em salas específicas
    candidatos_fixos = {
        # candidato_id: sala_id
    }

    # Cria um dicionário de listas por sala
    candidatos_por_sala = {sala: [] for sala in sala_ids}

    # Lista de candidatos disponíveis (todos menos os obrigatórios)
    candidatos_disponiveis = [c for c in candidatos if c.id not in candidatos_fixos]

    for sala_id in sala_ids:
        # Adiciona os candidatos obrigatórios dessa sala
        for candidato_id, sala_obrigatoria in candidatos_fixos.items():
            if sala_obrigatoria == sala_id:
                candidato = next(c for c in candidatos if c.id == candidato_id)
                candidatos_por_sala[sala_id].append(candidato)

        # Preenche o restante da sala com candidatos disponíveis
        while len(candidatos_por_sala[sala_id]) < limite_salas[sala_id] and candidatos_disponiveis:
            candidato = candidatos_disponiveis.pop(0)  # já ordenados por nome
            candidatos_por_sala[sala_id].append(candidato)

        # Ordena a sala pelo nome
        candidatos_por_sala[sala_id] = sorted(candidatos_por_sala[sala_id], key=lambda c: c.nome)

    # Salva as alocações
    for sala_id, candidatos_na_sala in candidatos_por_sala.items():
        sala = Sala.objects.get(id=sala_id)
        for candidato in candidatos_na_sala:
            aloca(candidato, sala)

    return HttpResponse("Alocação concluída.")

def aloca(candidato, sala):

    alocacao = Alocacao(edital=Edital.objects.get(id=4), sala=sala, candidato=candidato)
    alocacao.save()


def divulga(request):
    from django.http import HttpResponse

#    alocacoes = Alocacao.objects.filter(candidato__nome__gte='Wesley Laurindo De Santana')
    alocacoes = Alocacao.objects.all()

    print(alocacoes)

    for alocacao in alocacoes:
        envia_email(alocacao)


    return HttpResponse("Envio de e-mail concluído.")


def envia_email(alocacao):
    from django.template import Context
    from django.template.loader import render_to_string, get_template
    from django.core.mail import EmailMessage

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

#    mensagem = get_template('mail_alocacao.html').render(dados)
    mensagem = get_template('mail_alocacao2.html').render(dados)

    msg = EmailMessage(
        'Local e horário de prova',
        mensagem,
        'Escola de Auxiliares e Técnicos de Enfermagem Nossa Senhora de Fátima - Inscrição <inscricao@sme.novafriburgo.rj.gov.br>',
#        ['loyola@sme.novafriburgo.rj.gov.br',],
#        ['loyola@sme.novafriburgo.rj.gov.br', 'eenfermagemnsf@sme.novafriburgo.rj.gov.br'],
        [alocacao.candidato.email],
    )
    msg.content_subtype = "html"  # Main content is now text/html

    try:
        msg.send()
    except:
        print('Erro')
        print(dados)
        exit()


def confirmacao(request, chave):
    from ipware import get_client_ip

    candidato = Candidato.objects.get(chave=chave)
    alocacao = Alocacao.objects.get(candidato=candidato)

    # Busca IP

    client_ip, is_routable = get_client_ip(request)
    if client_ip is None:
        # Unable to get the client's IP address
        print(client_ip)
        client_ip = '0.0.0.0'
    else:
        # We got the client's IP address
        if is_routable:
            print('sim:', is_routable)
            # The client's IP address is publicly routable on the Internet
        else:
            print('não:', is_routable)
            # The client's IP address is privat

    acesso = Acesso(candidato=candidato, ip=client_ip)
    acesso.save()

    return render(request, 'confirmacao.html', { 'alocacao': alocacao })

def cadastro_notas(request):

    form = NotasForm()

    if request.method == 'POST':
        form = NotasForm(request.POST)

        if form.is_valid():
            id_candidato = form.cleaned_data['id_candidato']
            try:
                candidato = Candidato.objects.get(id=id_candidato)
            except ObjectDoesNotExist:
                messages.error(request, 'CPF não cadastrado.')
                return render(request, 'consulta.html', { 'form': form })

            try:
                nota = Nota.objects.get(candidato=candidato)
                form=NotasForm(request.POST, instance=nota)
                messages.success(request, "Nota atualizada com sucesso!")

            except:
                messages.success(request, "Nota cadastrada com sucesso!")
                
            nota = form.save()
            nota.candidato = candidato
            nota.save()
        else: 
            print('Erro: ', form.errors)
            erro_tmp = str(form.errors)
            erro_tmp = erro_tmp.replace('<ul class="errorlist">', '')
            erro_tmp = erro_tmp.replace('</li>', '')
            erro_tmp = erro_tmp.replace('<ul>', '')
            erro_tmp = erro_tmp.replace('</ul>', '')
            erro_tmp = erro_tmp.split('<li>')

            messages.error(request, erro_tmp[2])


    return render(request, 'cadastro_notas.html', {'form': form})
"""
def corrige_nome(request):

    candidatos = Candidato.objects.all()

    for candidato in candidatos:
        candidato.nome = candidato.nome.title()
        candidato.save()
"""
