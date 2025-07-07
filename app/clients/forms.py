
from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['company_name', 'internal_name', 'domain', 'contact_person', 'email']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'internal_name': forms.TextInput(attrs={'class': 'form-control'}),
            'domain': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }