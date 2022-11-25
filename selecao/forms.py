from django import forms
from django.forms import ModelForm, ValidationError
from .models import *
from .functions import validate_CPF


class ConsultaForm(forms.Form):
    cpf = forms.CharField(label='CPF', max_length=14, widget=forms.TextInput(
        attrs={'onkeydown': "mascara(this,icpf)"}))

    def clean_cpf(self):
        cpf = validate_CPF(self.cleaned_data["cpf"])
        return cpf


class CandidatoForm(ModelForm):
    DEFICIENCIA = (
        ('S', 'Sim'),
        ('N', 'Não'),
    )

    cpf = forms.CharField(label="CPF", max_length=14, widget=forms.TextInput(
        attrs={'onkeydown': "mascara(this,icpf)", 'onload': 'mascara(this,icpf)'}))
    celular = forms.CharField(label="Celular", max_length=15, widget=forms.TextInput(
        attrs={'onkeydown': "mascara(this,icelular)", 'onload': 'mascara(this,icelular)'}))
    tel = forms.CharField(label="Telefone", max_length=14, widget=forms.TextInput(attrs={
                          'onkeydown': "mascara(this,itelefone)", 'onload': 'mascara(this,itelefone)', 'required': False}))

    class Meta:
        model = Candidato
        widgets = {
            'edital': forms.HiddenInput(),
            'cpf': forms.TextInput(attrs={'onkeydown': "mascara(this,icpf)"}),
            'dt_nascimento': forms.SelectDateWidget(years=range(1940, 2022)),
        }
        exclude = ['chave', 'ip', 'dt_inclusao']

    def clean_cpf(self):
        cpf = validate_CPF(self.cleaned_data["cpf"])
        return cpf

    def clean_celular(self):
        telefone = self.cleaned_data["celular"]
        telefone = telefone.replace("(", '')
        telefone = telefone.replace(")", '')
        telefone = telefone.replace("-", '')
        telefone = telefone.replace(" ", '')
        if len(telefone) == 10:
            if telefone[2:3] != '2':
                raise ValidationError('Insira um número válido ')
        else:
            if len(telefone) != 11:
                raise ValidationError('Insira um número válido ')
        return telefone

    def clean_tel(self):
        telefone = self.cleaned_data["tel"]
        telefone = telefone.replace("(", '')
        telefone = telefone.replace(")", '')
        telefone = telefone.replace("-", '')
        telefone = telefone.replace(" ", '')
        if len(telefone) != 10 and len(telefone) != 0:
            raise ValidationError('Insira um número válido')
        return telefone

    def clean_email(self):
        email = self.cleaned_data["email"]

        if email.find('@') == -1:
            raise ValidationError('Insira um e-mail válido')

        return email

    def clean_deficiencia(self):
        if self.cleaned_data["deficiencia"] == 'S':
            if not self.data["qual_deficiencia"]:
                raise ValidationError(
                    {"qual_deficiencia": "Esse campo é obrigatório caso possua deficiência"})

            # if not self.data["file_termo_para_vagas_reservadas"]:
                # raise ValidationError({"file_termo_para_vagas_reservadas":"Esse campo é obrigatório caso possua deficiência"})

            # self.fields['qual_deficiencia'].widget.attrs['readonly'] = False
            # self.fields['necessidade'].widget.attrs['readonly'] = False
        else:
            # self.fields['qual_deficiencia'].widget.attrs['readonly'] = True
            # self.fields['necessidade'].widget.attrs['readonly'] = True
            pass

        return self.cleaned_data["deficiencia"]

    def clean_autodeclaracao(self):
        if self.cleaned_data["autodeclaracao"] == 'S':
            pass
            # if not self.data["file_termo_para_vagas_reservadas"]:
            #     raise ValidationError({"file_termo_para_vagas_reservadas":"Esse campo é obrigatório caso o candidato se autodeclara preto, pardo ou indígena"})
        else:
            pass

        return self.cleaned_data["autodeclaracao"]

    def clean_necessidade(self):
        if self.cleaned_data["necessidade"] == 'S':
            if not self.data["file_necessidade"]:
                raise ValidationError(
                    {"file_necessidade": "Esse campo é obrigatório caso o candidato necessite de alguma condição especial para a realização da prova"})
        else:
            pass

        return self.cleaned_data["necessidade"]

    def clean_tempo_excedente(self):
        if self.cleaned_data["tempo_excedente"] == 'S':
            if not self.data["file_tempo_excedente"]:
                raise ValidationError(
                    {"file_tempo_excedente": "Esse campo é obrigatório caso o candidato necessite de tempo excedente"})
        else:
            pass

        return self.cleaned_data["tempo_excedente"]

    def clean_ensino_fundamental_publico(self):
        if self.cleaned_data["ensino_fundamental_publico"] == 'S':
            pass
            # if not self.data["file_termo_para_vagas_reservadas"]:
            # raise ValidationError({"file_termo_para_vagas_reservadas":"Esse campo é obrigatório caso o candidato tenha cursado o ensino fundamental integralmente em escola pública"})
        else:
            pass

        return self.cleaned_data["ensino_fundamental_publico"]

    def clean_ensino_medio_publico(self):
        if self.cleaned_data["ensino_medio_publico"] == 'S':
            pass
            # if not self.data["file_termo_para_vagas_reservadas"]:
            # raise ValidationError({"file_termo_para_vagas_reservadas":"Esse campo é obrigatório caso o candidato tenha cursado o ensino médio integralmente em escola pública?"})
        else:
            pass

        return self.cleaned_data["ensino_medio_publico"]

    def clean_renda_bruta(self):
        if self.cleaned_data["renda_bruta"] == 'S':
            pass
            # if not self.data["file_termo_para_vagas_reservadas"]:
            # raise ValidationError({"file_termo_para_vagas_reservadas":"Esse campo é obrigatório caso o candidato possua renda menor que 1,5 salários mínimos per capita"})
        else:
            pass

        return self.cleaned_data["renda_bruta"]

    def clean_file_termo_para_vagas_reservadas(self):
        return self.cleaned_data['file_termo_para_vagas_reservadas'].name.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,/<>?\|`~-=_+"}).replace(' ', '')

    def clean_file_necessidade(self):
        return self.cleaned_data['file_necessidade'].name.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,/<>?\|`~-=_+"}).replace(' ', '')

    def clean_file_tempo_excedente(self):
        return self.cleaned_data['file_tempo_excedente'].name.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,/<>?\|`~-=_+"}).replace(' ', '')


class ContatoForm(forms.Form):
    nome = forms.CharField(label='Nome', max_length=60)
    cpf = forms.CharField(label='CPF', max_length=14, widget=forms.TextInput(
        attrs={'onkeydown': "mascara(this,icpf)"}))
    celular = forms.CharField(label="Celular", max_length=15, widget=forms.TextInput(
        attrs={'onkeydown': "mascara(this,icelular)", 'onload': 'mascara(this,icelular)'}))
    email = forms.CharField(label='E-Mail', max_length=200)
    duvida = forms.CharField(
        label='Dúvida', max_length=1000, widget=forms.Textarea(attrs={'size': '40'}))

    def clean_cpf(self):
        cpf = validate_CPF(self.cleaned_data["cpf"])
        return cpf

    def clean_celular(self):
        telefone = self.cleaned_data["celular"]
        telefone = telefone.replace("(", '')
        telefone = telefone.replace(")", '')
        telefone = telefone.replace("-", '')
        telefone = telefone.replace(" ", '')
        if len(telefone) == 10:
            if telefone[2:3] != '2':
                raise ValidationError('Insira um número válido ')
        else:
            if len(telefone) != 11:
                raise ValidationError('Insira um número válido ')
        return telefone


class NotasForm(ModelForm):

    cpf = forms.CharField(label='CPF do candidato', max_length=14, widget=forms.TextInput(
        attrs={'onkeydown': "mascara(this,icpf)"}))

    class Meta:
        model = Nota
        exclude = ['dt_inclusao']
        widgets = {
            'candidato': forms.HiddenInput()
        }

    def clean_cpf(self):
        cpf = validate_CPF(self.cleaned_data["cpf"])
        return cpf
