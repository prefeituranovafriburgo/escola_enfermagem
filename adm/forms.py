from django import forms
from django.forms import ModelForm, ValidationError
from .models import *

class BuscaNomeForm(forms.Form):

    nome = forms.CharField()
