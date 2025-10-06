from django import forms
from django.forms import ModelForm, ValidationError
from .models import *

class BuscaNomeForm(forms.Form):
    nome = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',  # deixa estilo Bootstrap
            'placeholder': 'Digite o nome',  # opcional, só pra UX
        })
    )
