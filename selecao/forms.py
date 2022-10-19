from django import forms
from django.forms import ModelForm, ValidationError
from .models import *
from .functions import validate_CPF

class ConsultaForm(forms.Form):
    cpf = forms.CharField(label='CPF', max_length=14, widget = forms.TextInput(attrs={'onkeydown':"mascara(this,icpf)"}))

    def clean_cpf(self):
        cpf = validate_CPF(self.cleaned_data["cpf"])
        return cpf


class CandidatoForm(ModelForm):
    DEFICIENCIA = (
        ('S', 'Sim'),
        ('N', 'Não'),
    )

    
    cpf = forms.CharField(label = "CPF", max_length=14, widget = forms.TextInput(attrs={'onkeydown':"mascara(this,icpf)", 'onload' : 'mascara(this,icpf)'}))
    celular = forms.CharField(label = "Celular", max_length=15, widget = forms.TextInput(attrs={'onkeydown':"mascara(this,icelular)", 'onload' : 'mascara(this,icelular)'}))
    tel = forms.CharField(label = "Telefone", max_length=14, widget = forms.TextInput(attrs={'onkeydown':"mascara(this,itelefone)", 'onload' : 'mascara(this,itelefone)'}))

    class Meta:
        model = Candidato
        widgets = {
            'edital': forms.HiddenInput(),
            'cpf': forms.TextInput(attrs={'onkeydown':"mascara(this,icpf)"}),
            'dt_nascimento': forms.SelectDateWidget(years=range(1940, 2022)),            
        }
        exclude = ['chave', 'ip', 'dt_inclusao']

    def clean_cpf(self):
        cpf = validate_CPF(self.cleaned_data["cpf"])
        return cpf

    def clean_celular(self):
        telefone = self.cleaned_data["celular"]
        telefone = telefone.replace("(",'')
        telefone = telefone.replace(")",'')
        telefone = telefone.replace("-",'')
        telefone = telefone.replace(" ",'')
        if len(telefone) == 10:
            if telefone[2:3] != '2':
                raise ValidationError('Insira um número válido ')
        else:
            if len(telefone) != 11:
                raise ValidationError('Insira um número válido ')
        return telefone
    
    def clean_tel(self):
        telefone = self.cleaned_data["tel"]
        telefone = telefone.replace("(",'')
        telefone = telefone.replace(")",'')
        telefone = telefone.replace("-",'')
        telefone = telefone.replace(" ",'')
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
            self.fields['qual_deficiencia'].widget.attrs['readonly'] = False
            self.fields['necessidade'].widget.attrs['readonly'] = False
        else:
            self.fields['qual_deficiencia'].widget.attrs['readonly'] = True
            self.fields['necessidade'].widget.attrs['readonly'] = True

        return self.cleaned_data["deficiencia"]


class ContatoForm(forms.Form):
    nome = forms.CharField(label='Nome', max_length=60)
    cpf = forms.CharField(label='CPF', max_length=14, widget = forms.TextInput(attrs={'onkeydown':"mascara(this,icpf)"}))
    celular = forms.CharField(label= "Celular", max_length=15, widget = forms.TextInput(attrs={'onkeydown':"mascara(this,icelular)", 'onload' : 'mascara(this,icelular)'}))
    email = forms.CharField(label='E-Mail', max_length=200)
    duvida = forms.CharField(label='Dúvida',max_length=1000,widget=forms.Textarea(attrs={'size': '40'}))

    def clean_cpf(self):
        cpf = validate_CPF(self.cleaned_data["cpf"])
        return cpf

    def clean_celular(self):
        telefone = self.cleaned_data["celular"]
        telefone = telefone.replace("(",'')
        telefone = telefone.replace(")",'')
        telefone = telefone.replace("-",'')
        telefone = telefone.replace(" ",'')
        if len(telefone) == 10:
            if telefone[2:3] != '2':
                raise ValidationError('Insira um número válido ')
        else:
            if len(telefone) != 11:
                raise ValidationError('Insira um número válido ')
        return telefone
