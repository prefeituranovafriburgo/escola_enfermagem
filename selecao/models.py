from email.policy import default
from django.db import models
from .functions import validate_CPF

# Create your models here.

class Edital(models.Model):

    CHOICES_MES = (
        ('JAN', 'Janeiro'),
        ('FEV', 'Fevereiro'),
        ('MAR', 'Março'),
        ('ABR', 'Abril'),
        ('MAI', 'Maio'),
        ('JUN', 'Junho'),
        ('JUL', 'Julho'),
        ('AGO', 'Agosto'),        
        ('SET', 'Setembro'),
        ('OUT', 'Outubro'),
        ('NOV', 'Novembro'),
        ('DEZ', 'Dezembro'),        
    )

    nome=models.CharField(max_length=90)
    mes=models.CharField(max_length=3, choices=CHOICES_MES)
    ano=models.CharField(max_length=4)
    vagas=models.IntegerField()
    vagas_reservadas=models.IntegerField()
    link_diario_oficial=models.URLField()
    descricao=models.TextField()
    dt_inicio_inscricao=models.DateField()
    dt_final_inscricao=models.DateField()
    dt_divulgacao=models.DateField(verbose_name='Data de divulgação do local e horário da prova')
    dt_prova=models.DateField()    
    dt_resultado=models.DateField()
    link_digulvacao=models.URLField(verbose_name='Link com local de prova e horário',blank=True, null=True)
    link_resultado=models.URLField(blank=True, null=True)
    ativo=models.BooleanField(default=True)
    dt_inclusao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s - %s/%s' % (self.nome, self.mes, self.ano)

    class Meta:
        ordering = ['-id']
        verbose_name_plural = "Editais"
        verbose_name = "Edital"
    
class Downloads(models.Model):
    nome=models.CharField(max_length=90)
    link=models.URLField()
    edital=models.ForeignKey(Edital, on_delete=models.CASCADE)
    dt_inclusao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s - %s' % (self.edital, self.nome)

    class Meta:
        ordering = ['-id']
        verbose_name_plural = "Downloads"
        verbose_name = "Download"
# Tabela para Candidato
class Candidato(models.Model):

    ESCOLHAS = (
        ('S', 'Sim'),
        ('N', 'Não'),
    )

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ['-id', 'nome']

    nome = models.CharField(verbose_name='Nome completo', max_length=60)
    dt_nascimento = models.DateField('Data de nascimento')
    cpf = models.CharField(verbose_name='CPF', unique=True, max_length=11, validators=[validate_CPF])
    celular = models.CharField(verbose_name='Celular', max_length=11)
    tel = models.CharField(verbose_name='Telefone', max_length=10, blank=True, null=True)
    email = models.CharField(verbose_name='Email', max_length=120)
    
    autodeclaracao=models.CharField(verbose_name='O candidato autodeclarado preto, pardo ou indígena', choices=ESCOLHAS, max_length=1)
    
    deficiencia = models.CharField(verbose_name='Possui deficiência?', max_length=1, choices=ESCOLHAS)
    qual_deficiencia = models.CharField(verbose_name='Indique qual a deficiência', max_length=600, blank=True, null=True)        
    necessidade = models.CharField(verbose_name='Informe se necessita de alguma condição especial para a realização da prova', max_length=200, blank=True)    
    tempo_excedente= models.CharField(verbose_name='Informe se necessita de tempo excedente para a realização da prova', max_length=200, blank=True)        
    
    ensino_fundamental_publico=models.CharField(verbose_name='O candidato cursou o ensino fundamental integralmente em escola pública?', choices=ESCOLHAS, max_length=1)
    ensino_medio_publico=models.CharField(verbose_name='O candidato cursou o ensino médio integralmente em escola pública?', choices=ESCOLHAS, max_length=1)
    renda_bruta=models.CharField(verbose_name='O candidato possui renda bruta mensal igual ou inferior a 1,5 salários mínimos per capita?', choices=ESCOLHAS, max_length=1)
    
    
    file_termo_para_vagas_reservadas=models.FileField(upload_to='file_adesao_sis_vagas_reservadas', verbose_name='Anexo em PDF do Termo de Adesão ao Sistema de Vagas Reservadas', blank=True, null=True)
    file_necessidade=models.FileField(upload_to='file_necessidade', verbose_name='Anexo em PDF de justificativa da necessidade por médico especializado', blank=True, null=True)
    file_tempo_excedente=models.FileField(upload_to='file_tempo_excedente', verbose_name='Anexo em PDF de justificativa para tempo excedente de médico especializado', blank=True, null=True)
    
    ip = models.GenericIPAddressField(protocol='IPv4')
    chave = models.CharField(unique=True, max_length=36)
    edital=models.ForeignKey(Edital, on_delete=models.CASCADE, null=True)
    dt_inclusao = models.DateTimeField(auto_now_add=True)


# Tabela para Local de Prova
class Local(models.Model):

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ['nome']
        verbose_name_plural = "Locais"

    nome = models.CharField(max_length=60)
    rua = models.CharField(max_length=60)
    numero = models.CharField(max_length=10)
    bairro = models.CharField(max_length=20)
    cidade = models.CharField(max_length=20)
    edital=models.ForeignKey(Edital, on_delete=models.CASCADE, null=True)
    dt_inclusao = models.DateTimeField(auto_now_add=True)


# Tabela para Horario
class Horario(models.Model):

    def __str__(self):
        return '%s - %s' % (self.local, self.horario)

    class Meta:
        ordering = ['local', 'horario']
        verbose_name_plural = "Horários"
        verbose_name = "Horário"

    local = models.ForeignKey(Local, on_delete=models.PROTECT)
    data = models.DateField()
    horario = models.TimeField()    
    dt_inclusao = models.DateTimeField(auto_now_add=True)


# Tabela para Sala
class Sala(models.Model):

    def __str__(self):
        return '%s - %s' % (self.horario, self.sala)

    class Meta:
        ordering = ['horario', 'sala']

    horario = models.ForeignKey(Horario, on_delete=models.PROTECT)
    sala = models.CharField(max_length=5)
    qnt_alocação=models.IntegerField(verbose_name='Quantas alocações é permitida?')
    deficiente=models.BooleanField(verbose_name='Adequado p/ deficiente')
    dt_inclusao = models.DateTimeField(auto_now_add=True)


# Tabela para Sala
class Alocacao(models.Model):

    def __str__(self):
        return '%s - %s' % (self.sala, self.candidato)

    class Meta:
        ordering = ['sala', 'candidato']
        verbose_name_plural = "Alocações"
        verbose_name = "Alocação"

    sala = models.ForeignKey(Sala, on_delete=models.PROTECT)
    candidato = models.ForeignKey(Candidato, on_delete=models.PROTECT)
    dt_inclusao = models.DateTimeField(auto_now_add=True)


# Tabela para registrar acessos ao comprovante
class Acesso(models.Model):

    def __str__(self):
        return '%s - %s' % (self.candidato, self.ip)

    class Meta:
        ordering = ['dt_inclusao']

    candidato = models.ForeignKey(Candidato, on_delete=models.PROTECT)
    ip = models.GenericIPAddressField(protocol='IPv4')
    dt_inclusao = models.DateTimeField(auto_now_add=True)
